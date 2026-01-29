import dataclasses
import enum
from collections import defaultdict

import pydantic.v1 as pydantic_v1
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
from werkzeug.exceptions import NotFound

from pcapi.connectors.serialization import titelive_serializers
from pcapi.connectors.titelive import GtlIdError
from pcapi.connectors.titelive import get_by_ean13
from pcapi.core.categories import subcategories
from pcapi.core.criteria import models as criteria_models
from pcapi.core.fraud import models as fraud_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers.titelive_book_search import get_ineligibility_reasons
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.filters import pluralize
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.utils import requests
from pcapi.utils.transaction_manager import mark_transaction_as_invalid

from . import forms


list_products_blueprint = utils.child_backoffice_blueprint(
    "product",
    __name__,
    url_prefix="/catalogue/product",
    permission=perm_models.Permissions.READ_OFFERS,
)


class ProductDetailsActionType(enum.StrEnum):
    SYNCHRO_TITELIVE = enum.auto()
    WHITELIST = enum.auto()
    BLACKLIST = enum.auto()
    TAG_MULTIPLE_OFFERS = enum.auto()


@dataclasses.dataclass
class ProductDetailsAction:
    type: ProductDetailsActionType
    position: int
    inline: bool


class ProductDetailsActions:
    def __init__(self, threshold: int) -> None:
        self.current_pos = 0
        self.actions: list[ProductDetailsAction] = []
        self.threshold = threshold

    def add_action(self, action_type: ProductDetailsActionType) -> None:
        self.actions.append(
            ProductDetailsAction(type=action_type, position=self.current_pos, inline=self.current_pos < self.threshold)
        )
        self.current_pos += 1

    def __contains__(self, action_type: ProductDetailsActionType) -> bool:
        return action_type in [e.type for e in self.actions]

    @property
    def inline_actions(self) -> list[ProductDetailsActionType]:
        return [action.type for action in self.actions if action.inline]

    @property
    def additional_actions(self) -> list[ProductDetailsActionType]:
        return [action.type for action in self.actions if not action.inline]


def _get_product_details_actions(threshold: int) -> ProductDetailsActions:
    product_details_actions = ProductDetailsActions(threshold)
    if utils.has_current_user_permission(perm_models.Permissions.PRO_FRAUD_ACTIONS):
        product_details_actions.add_action(ProductDetailsActionType.SYNCHRO_TITELIVE)
        product_details_actions.add_action(ProductDetailsActionType.WHITELIST)
        product_details_actions.add_action(ProductDetailsActionType.BLACKLIST)
    if utils.has_current_user_permission(perm_models.Permissions.MULTIPLE_OFFERS_ACTIONS):
        product_details_actions.add_action(ProductDetailsActionType.TAG_MULTIPLE_OFFERS)
    return product_details_actions


def _get_current_criteria_on_active_offers(offers: list[offers_models.Offer]) -> dict[criteria_models.Criterion, int]:
    current_criteria_on_offers: defaultdict[criteria_models.Criterion, int] = defaultdict(int)
    for offer in offers:
        if offer.isActive:
            for criterion in offer.criteria:
                current_criteria_on_offers[criterion] += 1

    return dict(current_criteria_on_offers)


@list_products_blueprint.route("/<int:product_id>", methods=["GET"])
def get_product_details(product_id: int) -> utils.BackofficeResponse:
    common_options = [
        sa_orm.load_only(
            offers_models.Offer.id,
            offers_models.Offer.name,
            offers_models.Offer.dateCreated,
            offers_models.Offer.publicationDatetime,
            offers_models.Offer.bookingAllowedDatetime,
            offers_models.Offer.validation,
        ),
        sa_orm.selectinload(offers_models.Offer.stocks).options(
            sa_orm.load_only(
                offers_models.Stock.bookingLimitDatetime,
                offers_models.Stock.beginningDatetime,
                offers_models.Stock.quantity,
                offers_models.Stock.dnBookedQuantity,
                offers_models.Stock.isSoftDeleted,
            )
        ),
        sa_orm.joinedload(offers_models.Offer.venue).options(
            sa_orm.load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.isSoftDeleted,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
            )
        ),
        sa_orm.selectinload(offers_models.Offer.criteria).options(
            sa_orm.load_only(criteria_models.Criterion.name, criteria_models.Criterion.id)
        ),
    ]

    product = (
        db.session.query(offers_models.Product)
        .filter(offers_models.Product.id == product_id)
        .options(
            sa_orm.selectinload(offers_models.Product.offers).options(*common_options),
            sa_orm.selectinload(offers_models.Product.productMediations),
            sa_orm.joinedload(offers_models.Product.lastProvider),
        )
        .one_or_none()
    )

    if not product:
        raise NotFound()

    unlinked_offers = []
    if (
        product.ean
        or (product.extraData and product.extraData.get("visa"))
        or (product.extraData and product.extraData.get("allocineId"))
    ):
        unlinked_offers_query = (
            db.session.query(offers_models.Offer)
            .filter(offers_models.Offer.productId.is_(None))
            .options(*common_options)
            .order_by(offers_models.Offer.id)
        )
        identifier_type = product.identifierType
        if identifier_type == offers_models.ProductIdentifierType.EAN:
            unlinked_offers_query = unlinked_offers_query.filter(offers_models.Offer.ean == product.ean)
            unlinked_offers = unlinked_offers_query.all()
        # The allocineId data exists only for products. We need to find offers that have the visa of this product.
        elif (
            identifier_type == offers_models.ProductIdentifierType.ALLOCINE_ID
            and product.extraData
            and product.extraData.get("visa")
        ) or identifier_type == offers_models.ProductIdentifierType.VISA:
            assert product.extraData  # helps mypy
            unlinked_offers_query = unlinked_offers_query.filter(
                offers_models.Offer._extraData["visa"].astext == product.extraData["visa"]
            )
            unlinked_offers = unlinked_offers_query.all()

    all_offers = product.offers + unlinked_offers

    allowed_actions = _get_product_details_actions(threshold=4)

    active_offers_count = sum(offer.isActive for offer in all_offers)
    approved_active_offers_count = sum(
        1 for offer in all_offers if offer.validation == OfferValidationStatus.APPROVED and offer.isActive
    )
    approved_inactive_offers_count = sum(
        1 for offer in all_offers if offer.validation == OfferValidationStatus.APPROVED and not offer.isActive
    )
    pending_offers_count = sum(1 for offer in all_offers if offer.validation == OfferValidationStatus.PENDING)
    rejected_offers_count = sum(1 for offer in all_offers if offer.validation == OfferValidationStatus.REJECTED)

    titelive_data = {}
    ineligibility_reasons = None
    product_whitelist = None
    if product.ean:
        try:
            titelive_data = get_by_ean13(product.ean)
        except offers_exceptions.TiteLiveAPINotExistingEAN:
            pass
        except Exception as err:
            flash(
                Markup(
                    "Une erreur s’est produite lors de la récupération des informations via l’API Titelive: {message}"
                ).format(message=str(err) or err.__class__.__name__),
                "warning",
            )
        try:
            data = pydantic_v1.parse_obj_as(titelive_serializers.TiteLiveBookWork, titelive_data["oeuvre"])
        except Exception:
            pass
        else:
            ineligibility_reasons = get_ineligibility_reasons(data.article[0], data.titre)

        product_whitelist = (
            db.session.query(fraud_models.ProductWhitelist)
            .filter(fraud_models.ProductWhitelist.ean == product.ean)
            .options(
                sa_orm.load_only(
                    fraud_models.ProductWhitelist.ean,
                    fraud_models.ProductWhitelist.dateCreated,
                    fraud_models.ProductWhitelist.comment,
                    fraud_models.ProductWhitelist.authorId,
                ),
                sa_orm.joinedload(fraud_models.ProductWhitelist.author).load_only(
                    users_models.User.firstName, users_models.User.lastName
                ),
            )
            .one_or_none()
        )

    return render_template(
        "products/details.html",
        product=product,
        provider_name=product.lastProvider.name if product.lastProvider else None,
        allowed_actions=allowed_actions,
        action=ProductDetailsActionType,
        unlinked_offers=unlinked_offers,
        titelive_data=titelive_data,
        active_offers_count=active_offers_count,
        approved_active_offers_count=approved_active_offers_count,
        approved_inactive_offers_count=approved_inactive_offers_count,
        pending_offers_count=pending_offers_count,
        rejected_offers_count=rejected_offers_count,
        ineligibility_reasons=ineligibility_reasons,
        product_whitelist=product_whitelist,
        music_titelive_subcategories=subcategories.MUSIC_TITELIVE_SUBCATEGORY_SEARCH_IDS,
        current_criteria_on_offers=_get_current_criteria_on_active_offers(all_offers),
    )


@list_products_blueprint.route("/<int:product_id>/synchro_titelive", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_product_synchronize_with_titelive_form(product_id: int) -> utils.BackofficeResponse:
    product = db.session.query(offers_models.Product).filter_by(id=product_id).one_or_none()
    if not (product and product.ean):
        raise NotFound()

    try:
        titelive_data = get_by_ean13(product.ean)
    except Exception as err:
        mark_transaction_as_invalid()
        return render_template(
            "components/dynamic/modal_empty_form.html",
            div_id=f"synchro-product-modal-{product.id}",
            messages=[
                f"Une erreur s’est produite lors de la récupération des informations via l’API Titelive: {str(err) or err.__class__.__name__}"
            ],
        )
    try:
        data = pydantic_v1.parse_obj_as(titelive_serializers.TiteLiveBookWork, titelive_data["oeuvre"])
    except Exception:
        ineligibility_reasons = None
    else:
        ineligibility_reasons = get_ineligibility_reasons(data.article[0], data.titre)

    return render_template(
        "products/titelive_synchro_modal.html",
        form=empty_forms.EmptyForm(),
        dst=url_for(".synchronize_product_with_titelive", product_id=product_id),
        title="Données récupérées via l'API Titelive",
        titelive_data=titelive_data,
        div_id=f"synchro-product-modal-{product.id}",
        button_text="Mettre le produit à jour avec ces informations",
        ineligibility_reasons=ineligibility_reasons,
        product_whitelist=None,
    )


@list_products_blueprint.route("/<int:product_id>/synchro-titelive", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def synchronize_product_with_titelive(product_id: int) -> utils.BackofficeResponse:
    product = db.session.query(offers_models.Product).filter_by(id=product_id).one_or_none()
    if not (product and product.ean):
        raise NotFound()

    try:
        titelive_data = offers_api.get_new_product_from_ean13(product.ean)
        offers_api.fetch_or_update_product_with_titelive_data(titelive_data.product)
        offers_api.create_or_update_product_mediations(product, titelive_data.images)
    except requests.ExternalAPIException as err:
        mark_transaction_as_invalid()
        flash(
            Markup("Une erreur s'est produite : {message}").format(message=str(err) or err.__class__.__name__),
            "warning",
        )
    else:
        flash("Le produit a été synchronisé avec Titelive", "success")

    return redirect(request.referrer or url_for(".get_product_details", product_id=product_id), 303)


@list_products_blueprint.route("/<int:product_id>/whitelist", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_product_whitelist_form(product_id: int) -> utils.BackofficeResponse:
    product = db.session.query(offers_models.Product).filter_by(id=product_id).one_or_none()
    if not product:
        raise NotFound()

    form = empty_forms.EmptyForm()
    return render_template(
        "components/dynamic/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.product.whitelist_product", product_id=product.id),
        div_id=f"whitelist-product-modal-{product.id}",
        title=f"Whitelister le produit  {product.name}",
        button_text="Whitelister le produit",
        ajax_submit=False,
    )


@list_products_blueprint.route("/<int:product_id>/whitelist", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def whitelist_product(product_id: int) -> utils.BackofficeResponse:
    product = db.session.query(offers_models.Product).filter_by(id=product_id).one_or_none()
    if not product:
        raise NotFound()

    product.gcuCompatibilityType = offers_models.GcuCompatibilityType.COMPATIBLE
    flash("Le produit a été marqué compatible avec les CGU", "success")
    return redirect(request.referrer or url_for(".get_product_details", product_id=product_id), 303)


@list_products_blueprint.route("/<int:product_id>/blacklist", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_product_blacklist_form(product_id: int) -> utils.BackofficeResponse:
    product = db.session.query(offers_models.Product).filter_by(id=product_id).one_or_none()
    if not product:
        raise NotFound()

    form = empty_forms.EmptyForm()
    return render_template(
        "components/dynamic/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.product.blacklist_product", product_id=product.id),
        div_id=f"blacklist-product-modal-{product.id}",
        title=f"Blacklister le produit  {product.name}",
        button_text="Blacklister le produit",
        ajax_submit=False,
    )


@list_products_blueprint.route("/<int:product_id>/blacklist", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def blacklist_product(product_id: int) -> utils.BackofficeResponse:
    product = db.session.query(offers_models.Product).filter_by(id=product_id).one_or_none()
    if not (product and product.ean):
        raise NotFound()

    if offers_api.reject_inappropriate_products([product.ean], current_user, rejected_by_fraud_action=True):
        db.session.commit()
        flash("Le produit a été marqué incompatible avec les CGU et les offres ont été désactivées", "success")
    else:
        db.session.rollback()
        flash("Une erreur s'est produite lors de l'opération", "warning")

    return redirect(request.referrer or url_for(".get_product_details", product_id=product_id), 303)


@list_products_blueprint.route("/<int:product_id>/link_offers/confirm", methods=["GET", "POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def confirm_link_offers_forms(product_id: int) -> utils.BackofficeResponse:
    form = forms.BatchLinkOfferToProductForm()

    return render_template(
        "components/dynamic/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.product.batch_link_offers_to_product", product_id=product_id),
        div_id="batch-link-to-product-modal",
        title=Markup("Voulez-vous associer {number_of_offers} offre{pluralize} au produit ?").format(
            number_of_offers=len(form.object_ids_list), pluralize=pluralize(len(form.object_ids_list))
        ),
        button_text="Confirmer l'association",
        information=Markup("Vous allez associer {number_of_offers} offre{pluralize}. Voulez vous continuer ?").format(
            number_of_offers=len(form.object_ids_list), pluralize=pluralize(len(form.object_ids_list))
        ),
        ajax_submit=False,
    )


@list_products_blueprint.route("/<int:product_id>/link_offers", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def batch_link_offers_to_product(product_id: int) -> utils.BackofficeResponse:
    form = forms.BatchLinkOfferToProductForm()
    product = db.session.query(offers_models.Product).filter(offers_models.Product.id == product_id).one_or_none()
    if not product:
        raise NotFound()

    db.session.query(offers_models.Offer).filter(offers_models.Offer.id.in_(form.object_ids_list)).update(
        {
            "productId": product.id,
            "name": product.name,
            "_description": None,
            "_durationMinutes": None,
            "_extraData": {},
        },
    )
    flash(
        Markup("{pluralize} au produit avec succès").format(
            pluralize=pluralize(len(form.object_ids_list), "L'offre a été associée", "Les offres ont été associées"),
        ),
        "success",
    )
    return redirect(request.referrer or url_for(".get_product_details", product_id=product_id), 303)


@list_products_blueprint.route("/<int:product_id>/tag-offers", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MULTIPLE_OFFERS_ACTIONS)
def get_tag_offers_form(product_id: int) -> utils.BackofficeResponse:
    product = (
        db.session.query(offers_models.Product)
        .options(sa_orm.selectinload(offers_models.Product.offers))
        .get(product_id)
    )
    if not product:
        raise NotFound()

    linked_active_offers_count = sum(offer.isActive for offer in product.offers)

    unlinked_offers_query = db.session.query(offers_models.Offer).filter(
        offers_models.Offer.productId.is_(None), offers_models.Offer.isActive
    )

    identifier_type = product.identifierType
    if identifier_type == offers_models.ProductIdentifierType.EAN:
        unlinked_offers_query = unlinked_offers_query.filter(offers_models.Offer.ean == product.ean)
        identifier_string = " cet EAN-13"
    # The allocineId data exists only for products. We need to find offers that have the visa of this product.
    elif product.extraData and (
        (identifier_type == offers_models.ProductIdentifierType.ALLOCINE_ID and product.extraData.get("visa"))
        or identifier_type == offers_models.ProductIdentifierType.VISA
    ):
        unlinked_offers_query = unlinked_offers_query.filter(
            offers_models.Offer._extraData["visa"].astext == product.extraData["visa"]
        )
        identifier_string = (
            "ce visa" if identifier_type == offers_models.ProductIdentifierType.VISA else "cet ID Allociné"
        )

    unlinked_active_offers_count = unlinked_offers_query.count()

    total_active_offers_count = linked_active_offers_count + unlinked_active_offers_count
    form = forms.OfferCriteriaForm()
    information_message = None
    if total_active_offers_count > 0:
        message_part = pluralize(
            total_active_offers_count,
            singular=f"offre active associée à {identifier_string} sera affectée",
            plural=f"offres actives associées à {identifier_string} seront affectées",
        )
        information_message = Markup("⚠️ {} {}").format(total_active_offers_count, message_part)

    return render_template(
        "components/dynamic/modal_form.html",
        form=form,
        dst=url_for(".add_criteria_to_offers", product_id=product_id),
        div_id=f"tag-offers-product-modal-{product.id}",
        title="Tag des offres",
        button_text="Enregistrer",
        information=information_message,
        ajax_submit=False,
    )


@list_products_blueprint.route("/<int:product_id>/add-criteria", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MULTIPLE_OFFERS_ACTIONS)
def add_criteria_to_offers(product_id: int) -> utils.BackofficeResponse:
    product = db.session.query(offers_models.Product).get(product_id)
    if not product:
        raise NotFound()

    form = forms.OfferCriteriaForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")

    identifier_type = product.identifierType
    if identifier_type == offers_models.ProductIdentifierType.EAN:
        success = offers_api.add_criteria_to_offers(form.criteria.data, ean=product.ean)
    # The allocineId data exists only for products. We need to find offers that have the visa of this product.
    elif product.extraData and (
        (identifier_type == offers_models.ProductIdentifierType.ALLOCINE_ID and product.extraData.get("visa"))
        or identifier_type == offers_models.ProductIdentifierType.VISA
    ):
        success = offers_api.add_criteria_to_offers(form.criteria.data, visa=product.extraData["visa"])

    if success:
        flash("Les offres du produit ont été taguées", "success")
    else:
        flash("Une erreur s'est produite lors de l'opération", "warning")

    return redirect(url_for(".get_product_details", product_id=product_id), 303)


def render_search_template(form: forms.ProductSearchForm | None = None) -> str:
    if form is None:
        form = forms.ProductSearchForm()

    return render_template(
        "products/search.html",
        title="Recherche produit",
        dst=url_for(".search_product"),
        form=form,
    )


@list_products_blueprint.route("/search", methods=["GET"])
def search_product() -> utils.BackofficeResponse:
    if not request.args:
        return render_search_template()

    form = forms.ProductSearchForm(request.args)
    if not form.validate():
        return render_search_template(form), 400

    result_type = forms.ProductFilterTypeEnum[form.product_filter_type.data]
    search_query = form.q.data

    product = None
    FILTER_MAP = {
        forms.ProductFilterTypeEnum.VISA: offers_models.Product.extraData["visa"].astext,
        forms.ProductFilterTypeEnum.ALLOCINE_ID: offers_models.Product.extraData["allocineId"],
    }

    if result_type == forms.ProductFilterTypeEnum.ALLOCINE_ID:
        search_query = str(int(search_query))  # remove leading zeros

    if result_type in FILTER_MAP:
        field_to_filter = FILTER_MAP[result_type]
        product = db.session.query(offers_models.Product).filter(field_to_filter == search_query).one_or_none()
    elif result_type == forms.ProductFilterTypeEnum.EAN:
        ean = search_query
        product = db.session.query(offers_models.Product).filter_by(ean=ean).one_or_none()
        if not product:
            titelive_data = {}
            try:
                titelive_data = get_by_ean13(ean)
            except offers_exceptions.TiteLiveAPINotExistingEAN:
                pass
            except Exception as err:
                flash(
                    Markup(
                        "Une erreur s’est produite lors de la récupération des informations via l’API Titelive : {message}"
                    ).format(message=str(err) or err.__class__.__name__),
                    "warning",
                )
            try:
                data = pydantic_v1.parse_obj_as(titelive_serializers.TiteLiveBookWork, titelive_data["oeuvre"])
            except Exception:
                titelive_data = {}
                ineligibility_reason = None
            else:
                ineligibility_reason = get_ineligibility_reasons(data.article[0], data.titre)

            return render_template(
                "products/search_product_result.html",
                form=form,
                dst=url_for(".search_product"),
                is_ean_product=True,
                titelive_data=titelive_data,
                ineligibility_reason=ineligibility_reason,
                button_text="Importer ce produit dans la base de données du pass Culture",
            )

    if not product:
        return render_template(
            "products/search_product_result.html",
            form=form,
            dst=url_for(".search_product"),
        )

    return redirect(url_for(".get_product_details", product_id=product.id), 303)


@list_products_blueprint.route("/<string:ean>/import_titelive_product_form", methods=["GET", "POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_import_product_from_titelive_form(ean: str) -> utils.BackofficeResponse:
    is_ineligible = request.args.get("is_ineligible", "false").lower() == "true"
    if is_ineligible:
        form = forms.CommentForm()
    else:
        form = empty_forms.EmptyForm()

    return render_template(
        "components/dynamic/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.product.import_product_from_titelive", ean=ean, is_ineligible=is_ineligible),
        div_id="import-product-modal",
        title="Voulez-vous importer ce produit ?",
        button_text="Importer",
        ajax_submit=False,
    )


@list_products_blueprint.route("/<string:ean>/import_titelive_product", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def import_product_from_titelive(ean: str) -> utils.BackofficeResponse:
    is_ineligible = request.args.get("is_ineligible", "false").lower() == "true"

    try:
        product = offers_api.whitelist_product(ean, update_images=True)
    except offers_exceptions.TiteLiveAPINotExistingEAN:
        flash(Markup("L'EAN <b>{ean}</b> n'existe pas chez Titelive").format(ean=ean), "warning")
    except GtlIdError:
        flash(
            Markup("L'EAN <b>{ean}</b> n'a pas de GTL ID chez Titelive").format(ean=ean),
            "warning",
        )
    else:
        if is_ineligible:
            try:
                if product.ean:
                    form = forms.CommentForm()
                    product_whitelist = fraud_models.ProductWhitelist(
                        comment=form.comment.data, ean=product.ean, title=product.name, authorId=current_user.id
                    )
                    db.session.add(product_whitelist)
                    db.session.flush()
            except sa.exc.IntegrityError as error:
                mark_transaction_as_invalid()
                flash(
                    Markup("L'EAN <b>{ean}</b> n'a pas été ajouté dans la whitelist :<br/>{error}").format(
                        ean=ean, error=error
                    ),
                    "warning",
                )
            except GtlIdError:
                mark_transaction_as_invalid()
                flash(
                    Markup("L'EAN <b>{ean}</b> n'a pas de GTL ID côté Titelive").format(ean=ean),
                    "warning",
                )
            else:
                flash(Markup("L'EAN <b>{ean}</b> a été ajouté dans la whitelist").format(ean=ean), "success")

                if product:
                    offers_api.revalidate_offers_after_product_whitelist(product, current_user)

        flash(Markup("Le produit <b>{product_name}</b> a été créé").format(product_name=product.name), "success")
        return redirect(url_for(".get_product_details", product_id=product.id), 303)

    return redirect(request.referrer or url_for(".search_product"), 303)
