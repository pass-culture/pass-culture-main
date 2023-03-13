from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.core.categories import subcategories_v2
from pcapi.core.criteria import models as criteria_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.repository import repository
from pcapi.utils.clean_accents import clean_accents

from . import autocomplete
from . import utils
from .forms import offer as offer_forms


list_offers_blueprint = utils.child_backoffice_blueprint(
    "offer",
    __name__,
    url_prefix="/pro/offer",
    permission=perm_models.Permissions.MANAGE_OFFERS,
)


def _get_offers(form: offer_forms.GetOffersListForm) -> list[offers_models.Offer]:
    base_query = offers_models.Offer.query.options(
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

    if form.criteria.data:
        base_query = base_query.outerjoin(offers_models.Offer.criteria).filter(
            criteria_models.Criterion.id.in_(form.criteria.data)
        )

    if form.category.data:
        base_query = base_query.filter(
            offers_models.Offer.subcategoryId.in_(
                subcategory.id
                for subcategory in subcategories_v2.ALL_SUBCATEGORIES
                if subcategory.category.id in form.category.data
            )
        )

    if form.department.data:
        base_query = base_query.join(offers_models.Offer.venue).filter(
            offerers_models.Venue.departementCode.in_(form.department.data)
        )

    if form.venue.data:
        base_query = base_query.filter(offers_models.Offer.venueId.in_(form.venue.data))

    if form.q.data:
        search_query = form.q.data
        or_filters = []

        if form.where.data == offer_forms.OfferSearchColumn.ISBN.name or (
            form.where.data == offer_forms.OfferSearchColumn.ALL.name and utils.is_isbn_valid(search_query)
        ):
            or_filters.append(offers_models.Offer.extraData["isbn"].astext == utils.format_isbn_or_visa(search_query))

        if form.where.data == offer_forms.OfferSearchColumn.VISA.name or (
            form.where.data == offer_forms.OfferSearchColumn.ALL.name and utils.is_visa_valid(search_query)
        ):
            or_filters.append(offers_models.Offer.extraData["visa"].astext == utils.format_isbn_or_visa(search_query))

        if (
            form.where.data in (offer_forms.OfferSearchColumn.ALL.name, offer_forms.OfferSearchColumn.ID.name)
            and search_query.isnumeric()
        ):
            or_filters.append(offers_models.Offer.id == int(search_query))

        if form.where.data == offer_forms.OfferSearchColumn.NAME.name or (
            form.where.data == offer_forms.OfferSearchColumn.ALL.name and not or_filters
        ):
            name_query = search_query.replace(" ", "%").replace("-", "%")
            name_query = clean_accents(name_query)
            or_filters.append(sa.func.unaccent(offers_models.Offer.name).ilike(f"%{name_query}%"))

        if or_filters:
            query = base_query.filter(or_filters[0])
            if len(or_filters) > 1:
                # Same as for bookings, where union has better performance than or_
                query = query.union(*(base_query.filter(f) for f in or_filters[1:]))
        else:
            # Fallback, no result -- this should not happen when validate_q() checks searched string
            query = base_query.filter(False)
    else:
        query = base_query

    # +1 to check if there are more results than requested
    return query.limit(form.limit.data + 1).all()


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


@list_offers_blueprint.route("/<int:offer_id>/edit", methods=["GET"])
def get_edit_offer_form(offer_id: int) -> utils.BackofficeResponse:
    offer = (
        offers_models.Offer.query.filter_by(id=offer_id)
        .options(
            sa.orm.joinedload(offers_models.Offer.criteria).load_only(
                criteria_models.Criterion.id, criteria_models.Criterion.name
            )
        )
        .one_or_none()
    )
    if not offer:
        raise NotFound()

    form = offer_forms.EditOfferForm()
    form.criteria.choices = [(criterion.id, criterion.name) for criterion in offer.criteria]
    if offer.rankingWeight:
        form.rankingWeight.data = offer.rankingWeight

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.offer.edit_offer", offer_id=offer.id),
        div_id=f"edit-offer-modal-{offer.id}",
        title=f"Édition de l'offre {offer.name}",
        button_text="Enregistrer les modifications",
    )


@list_offers_blueprint.route("/<int:offer_id>/edit", methods=["POST"])
def edit_offer(offer_id: int) -> utils.BackofficeResponse:
    offer = offers_models.Offer.query.get_or_404(offer_id)
    form = offer_forms.EditOfferForm()

    if not form.validate():
        flash("Le formulaire n'est pas valide", "error")
        return redirect(request.referrer, 400)

    criteria = criteria_models.Criterion.query.filter(criteria_models.Criterion.id.in_(form.criteria.data)).all()

    offer.criteria = criteria
    offer.rankingWeight = form.rankingWeight.data
    repository.save(offer)

    flash("L'offre a été modifiée avec succès", "success")
    return redirect(request.environ.get("HTTP_REFERER", url_for("backoffice_v3_web.offer.list_offers")), 303)


@list_offers_blueprint.route("", methods=["GET"])
def list_offers() -> utils.BackofficeResponse:
    form = offer_forms.GetOffersListForm(request.args)
    if not form.validate():
        return render_template("offer/list.html", rows=[], form=form), 400

    if form.is_empty():
        return render_template("offer/list.html", rows=[], form=form)

    offers = _get_offers(form)

    if len(offers) > form.limit.data:
        flash(
            f"Il y a plus de {form.limit.data} résultats dans la base de données, la liste ci-dessous n'en donne donc "
            "qu'une partie. Veuillez affiner les filtres de recherche.",
            "info",
        )
        offers = offers[: form.limit.data]

    autocomplete.prefill_criteria_choices(form.criteria)
    autocomplete.prefill_venues_choices(form.venue)

    return render_template(
        "offer/list.html",
        rows=offers,
        form=form,
        get_initial_stock=_get_initial_stock,
        get_remaining_stock=_get_remaining_stock,
    )
