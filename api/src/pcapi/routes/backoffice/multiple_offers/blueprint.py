from collections import defaultdict
import typing

from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from flask_login import current_user
import sqlalchemy as sa

from pcapi.core.criteria import models as criteria_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.repository import atomic

from . import forms
from .. import utils


multiple_offers_blueprint = utils.child_backoffice_blueprint(
    "multiple_offers",
    __name__,
    url_prefix="/pro/multiple-offers",
    permission=perm_models.Permissions.READ_OFFERS,
)


def _get_current_criteria_on_active_offers(offers: list[offers_models.Offer]) -> dict[criteria_models.Criterion, int]:
    current_criteria_on_offers: defaultdict[criteria_models.Criterion, int] = defaultdict(int)
    for offer in offers:
        if offer.isActive:
            for criterion in offer.criteria:
                current_criteria_on_offers[criterion] += 1

    return dict(current_criteria_on_offers)


def _render_search(search_form: forms.SearchEanForm, **kwargs: typing.Any) -> str:
    if kwargs:
        return render_template(
            "multiple_offers/search_result.html", form=search_form, dst=url_for(".search_multiple_offers"), **kwargs
        )

    return render_template("multiple_offers/search.html", form=search_form, dst=url_for(".search_multiple_offers"))


@multiple_offers_blueprint.route("/", methods=["GET"])
@atomic()
def multiple_offers_home() -> utils.BackofficeResponse:
    form = forms.SearchEanForm()
    return _render_search(form)


@multiple_offers_blueprint.route("/search", methods=["GET"])
@atomic()
def search_multiple_offers() -> utils.BackofficeResponse:
    form = forms.SearchEanForm(formdata=utils.get_query_params())

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _render_search(form), 400

    ean = form.ean.data

    product = offers_models.Product.query.filter(
        offers_models.Product.extraData["ean"].astext == ean, offers_models.Product.idAtProviders.is_not(None)
    ).one_or_none()

    if not product:
        flash("Aucun produit n'a été trouvé avec cet EAN-13", "warning")
        return _render_search(form)

    offers = (
        offers_models.Offer.query.filter(
            sa.or_(offers_models.Offer.extraData["ean"].astext == ean, offers_models.Offer.productId == product.id)
        )
        .options(
            sa.orm.load_only(offers_models.Offer.isActive, offers_models.Offer.validation)
            .joinedload(offers_models.Offer.criteria)
            .load_only(criteria_models.Criterion.name),
            sa.orm.joinedload(offers_models.Offer.product),
        )
        .all()
    )

    active_offers_count = sum(offer.isActive for offer in offers)
    approved_active_offers_count = sum(
        offer.validation == OfferValidationStatus.APPROVED and offer.isActive for offer in offers
    )
    approved_inactive_offers_count = sum(
        offer.validation == OfferValidationStatus.APPROVED and not offer.isActive for offer in offers
    )
    pending_offers_count = sum(offer.validation == OfferValidationStatus.PENDING for offer in offers)
    rejected_offers_count = sum(offer.validation == OfferValidationStatus.REJECTED for offer in offers)

    operations_forms = {}

    if utils.has_current_user_permission(perm_models.Permissions.PRO_FRAUD_ACTIONS) and (
        product.isGcuCompatible
        or approved_active_offers_count + approved_inactive_offers_count + pending_offers_count > 0
    ):
        operations_forms["incompatibility_form"] = forms.HiddenEanForm(ean=ean)

    if utils.has_current_user_permission(perm_models.Permissions.MULTIPLE_OFFERS_ACTIONS):
        operations_forms["offer_criteria_form"] = forms.OfferCriteriaForm(ean=ean)

    return _render_search(
        form,
        name=product.name,
        category=product.subcategory.category,
        offers_count=len(offers),
        active_offers_count=active_offers_count,
        approved_active_offers_count=approved_active_offers_count,
        approved_inactive_offers_count=approved_inactive_offers_count,
        pending_offers_count=pending_offers_count,
        rejected_offers_count=rejected_offers_count,
        ean=ean,
        product_compatibility=product.gcuCompatibilityType.value,
        current_criteria_on_offers=_get_current_criteria_on_active_offers(offers),
        **operations_forms,
    )


@multiple_offers_blueprint.route("/add-criteria", methods=["POST"])
@atomic()
@utils.permission_required(perm_models.Permissions.MULTIPLE_OFFERS_ACTIONS)
def add_criteria_to_offers() -> utils.BackofficeResponse:
    form = forms.OfferCriteriaForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
    elif offers_api.add_criteria_to_offers(form.criteria.data, ean=form.ean.data):
        flash("Les offres du produit ont été taguées", "success")
    else:
        flash("Une erreur s'est produite lors de l'opération", "warning")

    return redirect(url_for(".search_multiple_offers", ean=form.ean.data), code=303)


@multiple_offers_blueprint.route("/set-product-gcu-incompatible", methods=["POST"])
@atomic()
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def set_product_gcu_incompatible() -> utils.BackofficeResponse:
    form = forms.HiddenEanForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
    elif offers_api.reject_inappropriate_products([form.ean.data], current_user, rejected_by_fraud_action=True):
        flash("Le produit a été rendu incompatible aux CGU et les offres ont été désactivées", "success")
    else:
        flash("Une erreur s'est produite lors de l'opération", "warning")

    return redirect(url_for(".search_multiple_offers", ean=form.ean.data), code=303)
