from flask import render_template
from flask import request

from pcapi.core.offers import models as offers_models
from pcapi.core.offers import repository as offers_repository
from pcapi.core.permissions import models as perm_models

from . import utils
from .forms import offer as offer_forms


MAX_OFFERS = 101

list_offers_blueprint = utils.child_backoffice_blueprint(
    "offer",
    __name__,
    url_prefix="/pro/offer",
    permission=perm_models.Permissions.MANAGE_OFFERS,
)


def _get_initial_stock(offer: offers_models.Offer) -> int | str:
    quantities = [stock.quantity for stock in offer.bookableStocks]
    if None in quantities:
        return "Illimité"
    # only integers in quantities
    return sum(quantities)  # type: ignore [arg-type]


def _get_remaining_stock(offer: offers_models.Offer) -> int | str:
    remaining_quantities = [stock.remainingQuantity for stock in offer.bookableStocks]
    if "unlimited" in remaining_quantities:
        return "Illimité"
    # only integers in remaining_quantities
    return sum(remaining_quantities)  # type: ignore [arg-type]


@list_offers_blueprint.route("", methods=["GET"])
def list_offers() -> utils.BackofficeResponse:
    form = offer_forms.GetOffersListForm(request.args)
    if not form.validate():
        return render_template("offer/list.html", rows=[], form=form), 400

    if not form.q.data:
        return render_template("offer/list.html", rows=[], form=form)

    offers = offers_repository.search_offers_by_filters(form.q.data, limit=MAX_OFFERS).all()

    return render_template(
        "offer/list.html",
        rows=offers,
        form=form,
        get_initial_stock=_get_initial_stock,
        get_remaining_stock=_get_remaining_stock,
    )
