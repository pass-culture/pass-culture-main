from flask import flash
from flask import render_template
from flask import request
import sqlalchemy as sa

from pcapi.core.categories import subcategories_v2
from pcapi.core.criteria import models as criteria_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.utils.clean_accents import clean_accents

from . import autocomplete
from . import utils
from .forms import offer as offer_forms


MAX_OFFERS = 101

list_offers_blueprint = utils.child_backoffice_blueprint(
    "offer",
    __name__,
    url_prefix="/pro/offer",
    permission=perm_models.Permissions.MANAGE_OFFERS,
)


def _get_offers(
    form: offer_forms.GetOffersListForm,
    limit: int,
) -> list[offers_models.Offer]:
    query = offers_models.Offer.query.options(
        sa.orm.load_only(
            offers_models.Offer.id,
            offers_models.Offer.name,
            offers_models.Offer.subcategoryId,
            offers_models.Offer.rankingWeight,
            offers_models.Offer.validation,
            offers_models.Offer.lastValidationDate,
            offers_models.Offer.isActive,
        ),
        sa.orm.joinedload(offers_models.Offer.stocks).load_only(
            offers_models.Stock.offerId,
            # needed to check if stock is bookable and compute initial/remaining stock:
            offers_models.Stock.beginningDatetime,
            offers_models.Stock.bookingLimitDatetime,
            offers_models.Stock.isSoftDeleted,
            offers_models.Stock.quantity,
            offers_models.Stock.dnBookedQuantity,
        ),
        sa.orm.joinedload(offers_models.Offer.criteria).load_only(criteria_models.Criterion.name),
        sa.orm.joinedload(offers_models.Offer.venue).load_only(
            offerers_models.Venue.managingOffererId, offerers_models.Venue.departementCode, offerers_models.Venue.name
        )
        # needed to check if stock is bookable and compute initial/remaining stock:
        .joinedload(offerers_models.Venue.managingOfferer).load_only(
            offerers_models.Offerer.isActive, offerers_models.Offerer.validationStatus
        ),
    )

    if form.q.data:
        search_query = form.q.data

        if search_query.isnumeric():
            query = query.filter(offers_models.Offer.id == int(search_query))
        else:
            name_query = search_query.replace(" ", "%").replace("-", "%")
            name_query = clean_accents(name_query)
            query = query.filter(sa.func.unaccent(offers_models.Offer.name).ilike(f"%{name_query}%"))

    if form.criteria.data:
        query = query.outerjoin(offers_models.Offer.criteria).filter(
            criteria_models.Criterion.id.in_(form.criteria.data)
        )

    if form.category.data:
        query = query.filter(
            offers_models.Offer.subcategoryId.in_(
                subcategory.id
                for subcategory in subcategories_v2.ALL_SUBCATEGORIES
                if subcategory.category.id in form.category.data
            )
        )

    if form.department.data:
        query = query.join(offers_models.Offer.venue).filter(
            offerers_models.Venue.departementCode.in_(form.department.data)
        )

    if form.venue.data:
        query = query.filter(offers_models.Offer.venueId.in_(form.venue.data))

    return query.limit(limit).all()


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

    if form.is_empty():
        return render_template("offer/list.html", rows=[], form=form)

    offers = _get_offers(form, limit=MAX_OFFERS)

    if len(offers) >= MAX_OFFERS:
        flash(
            f"Il y a plus de {MAX_OFFERS - 1} résultats dans la base de données, la liste ci-dessous n'en donne donc "
            "qu'une partie. Veuillez affiner les filtres de recherche.",
            "info",
        )

    autocomplete.prefill_criteria_choices(form.criteria)
    autocomplete.prefill_venues_choices(form.venue)

    return render_template(
        "offer/list.html",
        rows=offers,
        form=form,
        get_initial_stock=_get_initial_stock,
        get_remaining_stock=_get_remaining_stock,
    )
