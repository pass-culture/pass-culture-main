import dataclasses
import enum

import pydantic.v1 as pydantic_v1
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
from pcapi.connectors.titelive import get_by_ean13
from pcapi.core.fraud import models as fraud_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers.titelive_book_search import get_ineligibility_reasons
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.repository.session_management import mark_transaction_as_invalid
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.filters import pluralize
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.utils import requests

from . import forms


list_products_blueprint = utils.child_backoffice_blueprint(
    "product",
    __name__,
    url_prefix="/pro/product",
    permission=perm_models.Permissions.READ_OFFERS,
)


class ProductDetailsActionType(enum.StrEnum):
    SYNCHRO_TITELIVE = enum.auto()
    WHITELIST = enum.auto()
    BLACKLIST = enum.auto()


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
    return product_details_actions


@list_products_blueprint.route("/<int:product_id>", methods=["GET"])
def get_product_details(product_id: int) -> utils.BackofficeResponse:
    common_options = [
        sa_orm.load_only(
            offers_models.Offer.id,
            offers_models.Offer.name,
            offers_models.Offer.dateCreated,
            offers_models.Offer.isActive,
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
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
            )
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
    if product.ean:
        unlinked_offers = (
            db.session.query(offers_models.Offer)
            .filter(offers_models.Offer.ean == product.ean, offers_models.Offer.productId.is_(None))
            .options(*common_options)
            .order_by(offers_models.Offer.id)
            .all()
        )

    allowed_actions = _get_product_details_actions(threshold=4)

    active_offers_count = sum(offer.isActive for offer in product.offers)
    approved_active_offers_count = sum(
        1 for offer in product.offers if offer.validation == OfferValidationStatus.APPROVED and offer.isActive
    )
    approved_inactive_offers_count = sum(
        1 for offer in product.offers if offer.validation == OfferValidationStatus.APPROVED and not offer.isActive
    )
    pending_offers_count = sum(1 for offer in product.offers if offer.validation == OfferValidationStatus.PENDING)
    rejected_offers_count = sum(1 for offer in product.offers if offer.validation == OfferValidationStatus.REJECTED)

    if product.ean:
        try:
            titelive_data = get_by_ean13(product.ean)
        except Exception as err:
            flash(
                Markup(
                    "Une erreur s’est produite lors de la récupération des informations via l’API Titelive: {message}"
                ).format(message=str(err) or err.__class__.__name__),
                "warning",
            )
            titelive_data = {}
        try:
            data = pydantic_v1.parse_obj_as(titelive_serializers.TiteLiveBookWork, titelive_data["oeuvre"])
        except Exception:
            ineligibility_reasons = None
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
    else:
        titelive_data = None
        ineligibility_reasons = None
        product_whitelist = None

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
    )


@list_products_blueprint.route("/<int:product_id>/synchro_titelive", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_product_synchronize_with_titelive_form(product_id: int) -> utils.BackofficeResponse:
    product = db.session.query(offers_models.Product).filter_by(id=product_id).one_or_none()
    if not product:
        raise NotFound()

    try:
        titelive_data = get_by_ean13(product.ean)
    except Exception as err:
        mark_transaction_as_invalid()
        return render_template(
            "components/turbo/modal_empty_form.html",
            form=empty_forms.BatchForm(),
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
    if not product:
        raise NotFound()

    try:
        titelive_product = offers_api.get_new_product_from_ean13(product.ean)
        offers_api.fetch_or_update_product_with_titelive_data(titelive_product)
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
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.product.whitelist_product", product_id=product.id),
        div_id=f"whitelist-product-modal-{product.id}",
        title=f"Whitelister le produit  {product.name}",
        button_text="Whitelister le produit",
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
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.product.blacklist_product", product_id=product.id),
        div_id=f"blacklist-product-modal-{product.id}",
        title=f"Blacklister le produit  {product.name}",
        button_text="Blacklister le produit",
    )


@list_products_blueprint.route("/<int:product_id>/blacklist", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def blacklist_product(product_id: int) -> utils.BackofficeResponse:
    product = db.session.query(offers_models.Product).filter_by(id=product_id).one_or_none()
    if not product:
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
        "components/turbo/modal_form.html",
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
    )


@list_products_blueprint.route("/<int:product_id>/link_offers", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def batch_link_offers_to_product(product_id: int) -> utils.BackofficeResponse:
    form = forms.BatchLinkOfferToProductForm()
    product = db.session.query(offers_models.Product).get(product_id)
    db.session.query(offers_models.Offer).filter(offers_models.Offer.id.in_(form.object_ids_list)).update(
        {"productId": product.id, "name": product.name}
    )
    flash(
        Markup("{pluralize} au produit avec succès").format(
            pluralize=pluralize(len(form.object_ids_list), "L'offre a été associée", "Les offres ont été associées"),
        ),
        "success",
    )
    return redirect(request.referrer or url_for(".get_product_details", product_id=product_id), 303)
