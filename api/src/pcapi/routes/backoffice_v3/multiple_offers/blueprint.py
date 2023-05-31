from collections import defaultdict
import itertools
import typing

from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
import sqlalchemy as sa

from pcapi.core.criteria import models as criteria_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.models.offer_mixin import OfferValidationStatus

from . import forms
from .. import utils


multiple_offers_blueprint = utils.child_backoffice_blueprint(
    "multiple_offers",
    __name__,
    url_prefix="/pro/multiple-offers",
    permission=perm_models.Permissions.MULTIPLE_OFFERS_ACTIONS,
)


def _get_current_criteria_on_active_offers(offers: list[offers_models.Offer]) -> dict[criteria_models.Criterion, int]:
    current_criteria_on_offers: defaultdict[criteria_models.Criterion, int] = defaultdict(int)
    for offer in offers:
        if offer.isActive:
            for criterion in offer.criteria:
                current_criteria_on_offers[criterion] += 1

    return dict(current_criteria_on_offers)


def _get_products_compatible_status(products: list[offers_models.Product]) -> str:
    if all(product.isGcuCompatible for product in products):
        return "compatible_products"

    if all(not product.isGcuCompatible for product in products):
        return "incompatible_products"

    return "partially_incompatible_products"


def _render_search(search_form: forms.SearchEanForm, **kwargs: typing.Any) -> str:
    if kwargs:
        return render_template(
            "multiple_offers/search_result.html", form=search_form, dst=url_for(".search_multiple_offers"), **kwargs
        )

    return render_template("multiple_offers/search.html", form=search_form, dst=url_for(".search_multiple_offers"))


@multiple_offers_blueprint.route("/", methods=["GET"])
def multiple_offers_home() -> utils.BackofficeResponse:
    form = forms.SearchEanForm()
    return _render_search(form)


@multiple_offers_blueprint.route("/search", methods=["GET"])
def search_multiple_offers() -> utils.BackofficeResponse:
    form = forms.SearchEanForm(formdata=utils.get_query_params())

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _render_search(form), 400

    ean = form.ean.data

    products = (
        offers_models.Product.query.filter(offers_models.Product.extraData["ean"].astext == ean)
        .options(
            sa.orm.joinedload(offers_models.Product.offers)
            .load_only(offers_models.Offer.isActive, offers_models.Offer.validation)
            .joinedload(offers_models.Offer.criteria)
            .load_only(criteria_models.Criterion.name)
        )
        .all()
    )

    if not products:
        flash("Aucun livre n'a été trouvé avec cet EAN", "error")
        return _render_search(form)

    offers = list(itertools.chain.from_iterable(p.offers for p in products))

    active_offers_count = sum(offer.isActive for offer in offers)
    approved_active_offers_count = sum(
        offer.validation == OfferValidationStatus.APPROVED and offer.isActive for offer in offers
    )
    approved_inactive_offers_count = sum(
        offer.validation == OfferValidationStatus.APPROVED and not offer.isActive for offer in offers
    )
    pending_offers_count = sum(offer.validation == OfferValidationStatus.PENDING for offer in offers)
    rejected_offers_count = sum(offer.validation == OfferValidationStatus.REJECTED for offer in offers)

    return _render_search(
        form,
        name=products[0].name,
        category=products[0].subcategory.category,
        offers_count=len(offers),
        active_offers_count=active_offers_count,
        approved_active_offers_count=approved_active_offers_count,
        approved_inactive_offers_count=approved_inactive_offers_count,
        pending_offers_count=pending_offers_count,
        rejected_offers_count=rejected_offers_count,
        ean=ean,
        product_compatibility=_get_products_compatible_status(products),
        incompatibility_form=forms.HiddenEanForm(ean=ean),
        current_criteria_on_offers=_get_current_criteria_on_active_offers(offers),
        offer_criteria_form=forms.OfferCriteriaForm(ean=ean),
    )


@multiple_offers_blueprint.route("/add-criteria", methods=["POST"])
def add_criteria_to_offers() -> utils.BackofficeResponse:
    form = forms.OfferCriteriaForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
    elif offers_api.add_criteria_to_offers(form.criteria.data, ean=form.ean.data):
        flash("Les offres du produit ont bien été taguées", "success")
    else:
        flash("Une erreur s'est produite lors de l'opération", "warning")

    return redirect(url_for(".search_multiple_offers", ean=form.ean.data), code=303)


@multiple_offers_blueprint.route("/set-product-gcu-incompatible", methods=["POST"])
@utils.permission_required(perm_models.Permissions.FRAUD_ACTIONS)
def set_product_gcu_incompatible() -> utils.BackofficeResponse:
    form = forms.HiddenEanForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
    elif offers_api.reject_inappropriate_products(form.ean.data):
        flash("Le produit a été rendu incompatible aux CGU et les offres ont été désactivées", "success")
    else:
        flash("Une erreur s'est produite lors de l'opération", "warning")

    return redirect(url_for(".search_multiple_offers", ean=form.ean.data), code=303)
