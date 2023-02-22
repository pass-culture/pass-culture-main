import datetime
import re

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
import sqlalchemy as sa

from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import exceptions as bookings_exceptions
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories_v2
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.utils import date as date_utils
from pcapi.utils import email as email_utils
from pcapi.utils.clean_accents import clean_accents

from . import utils
from .forms import empty as empty_forms
from .forms import individual_booking as individual_booking_forms


individual_bookings_blueprint = utils.child_backoffice_blueprint(
    "individual_bookings",
    __name__,
    url_prefix="/individual-bookings",
    permission=perm_models.Permissions.READ_BOOKINGS,
)


BOOKING_TOKEN_RE = re.compile(r"^[A-Za-z0-9]{6}$")
NO_DIGIT_RE = re.compile(r"[^\d]+$")


def _get_individual_bookings(
    form: individual_booking_forms.GetIndividualBookingListForm,
) -> list[bookings_models.Booking]:
    base_query = (
        bookings_models.Booking.query.outerjoin(offers_models.Stock)
        .outerjoin(offers_models.Offer)
        .outerjoin(users_models.User, bookings_models.Booking.user)
        .options(
            sa.orm.joinedload(bookings_models.Booking.stock)
            .load_only(offers_models.Stock.quantity, offers_models.Stock.offerId)
            .joinedload(offers_models.Stock.offer)
            .load_only(
                offers_models.Offer.id,
                offers_models.Offer.name,
                offers_models.Offer.subcategoryId,
            ),
            sa.orm.joinedload(bookings_models.Booking.user).load_only(
                users_models.User.id, users_models.User.firstName, users_models.User.lastName
            ),
            sa.orm.joinedload(bookings_models.Booking.offerer).load_only(
                offerers_models.Offerer.id, offerers_models.Offerer.name
            ),
            sa.orm.joinedload(bookings_models.Booking.venue).load_only(
                # for name and link (build_pc_pro_venue_link)
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.isVirtual,
                offerers_models.Venue.managingOffererId,
            ),
            sa.orm.joinedload(bookings_models.Booking.pricings)
            .load_only(
                finance_models.Pricing.amount, finance_models.Pricing.status, finance_models.Pricing.creationDate
            )
            .joinedload(finance_models.Pricing.cashflows)
            .load_only(finance_models.Cashflow.batchId)
            .joinedload(finance_models.Cashflow.batch)
            .load_only(finance_models.CashflowBatch.label),
        )
    )

    if form.from_date.data:
        from_datetime = date_utils.date_to_localized_datetime(form.from_date.data, datetime.datetime.min.time())
        base_query = base_query.filter(bookings_models.Booking.dateCreated >= from_datetime)

    if form.to_date.data:
        to_datetime = date_utils.date_to_localized_datetime(form.to_date.data, datetime.datetime.max.time())
        base_query = base_query.filter(bookings_models.Booking.dateCreated <= to_datetime)

    if form.offerer.data:
        base_query = base_query.filter(bookings_models.Booking.offererId.in_(form.offerer.data))

    if form.venue.data:
        base_query = base_query.filter(bookings_models.Booking.venueId.in_(form.venue.data))

    if form.category.data:
        base_query = base_query.filter(
            offers_models.Offer.subcategoryId.in_(
                subcategory.id
                for subcategory in subcategories_v2.ALL_SUBCATEGORIES
                if subcategory.category.id in form.category.data
            )
        )

    if form.status.data:
        base_query = base_query.filter(bookings_models.Booking.status.in_(form.status.data))

    if form.q.data:
        search_query = form.q.data
        or_filters = []

        if BOOKING_TOKEN_RE.match(search_query):
            or_filters.append(bookings_models.Booking.token == search_query.upper())

            if NO_DIGIT_RE.match(search_query):
                flash(
                    f"Le critère de recherche « {search_query} » peut correspondre à un nom. Cependant, la recherche "
                    "n'a porté que sur les codes contremarques afin de répondre rapidement. Veuillez inclure prénom et "
                    "nom dans le cas d'un nom de 6 lettres.",
                    "info",
                )

        if search_query.isnumeric():
            or_filters.append(offers_models.Offer.id == int(search_query))
            or_filters.append(users_models.User.id == int(search_query))
        else:
            sanitized_email = email_utils.sanitize_email(search_query)
            if email_utils.is_valid_email(sanitized_email):
                or_filters.append(users_models.User.email == sanitized_email)

        if not or_filters:
            name = search_query.replace(" ", "%").replace("-", "%")
            name = clean_accents(name)
            or_filters.append(
                sa.func.unaccent(sa.func.concat(users_models.User.firstName, " ", users_models.User.lastName)).ilike(
                    f"%{name}%"
                ),
            )

        query = base_query.filter(or_filters[0])
        if len(or_filters) > 1:
            # Performance is really better than .filter(sa.or_(...)) when searching for a numeric id
            # On staging: or_ takes 19 minutes, union takes 0.15 second!
            query = query.union(*(base_query.filter(f) for f in or_filters[1:]))
    else:
        query = base_query

    # +1 to check if there are more results than requested
    return query.limit(form.limit.data + 1).all()


@individual_bookings_blueprint.route("", methods=["GET"])
def list_individual_bookings() -> utils.BackofficeResponse:
    form = individual_booking_forms.GetIndividualBookingListForm(request.args)
    if not form.validate():
        return render_template("individual_bookings/list.html", rows=[], form=form), 400

    if form.is_empty():
        # Empty results when no filter is set
        return render_template("individual_bookings/list.html", rows=[], form=form)

    bookings = _get_individual_bookings(form)

    if len(bookings) > form.limit.data:
        flash(
            f"Il y a plus de {form.limit.data} résultats dans la base de données, la liste ci-dessous n'en donne donc "
            "qu'une partie. Veuillez affiner les filtres de recherche.",
            "info",
        )
        bookings = bookings[: form.limit.data]

    if form.offerer.data:
        offerers = (
            offerers_models.Offerer.query.filter(offerers_models.Offerer.id.in_(form.offerer.data))
            .order_by(offerers_models.Offerer.name)
            .with_entities(
                offerers_models.Offerer.id,
                offerers_models.Offerer.name,
                offerers_models.Offerer.siren,
            )
        )
        form.offerer.choices = [(offerer_id, f"{name} ({siren})") for offerer_id, name, siren in offerers]

    if form.venue.data:
        venues = (
            offerers_models.Venue.query.filter(offerers_models.Venue.id.in_(form.venue.data))
            .order_by(offerers_models.Venue.name)
            .with_entities(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.siret,
            )
        )
        form.venue.choices = [(venue_id, f"{name} ({siret or 'Pas de SIRET'})") for venue_id, name, siret in venues]

    return render_template(
        "individual_bookings/list.html",
        rows=bookings,
        form=form,
        mark_as_used_booking_form=empty_forms.EmptyForm(),
        cancel_booking_form=empty_forms.EmptyForm(),
    )


def _redirect_after_individual_booking_action() -> utils.BackofficeResponse:
    if request.referrer:
        return redirect(request.referrer, code=303)

    return redirect(url_for("backoffice_v3_web.individual_bookings.list_individual_bookings"), code=303)


@individual_bookings_blueprint.route("/<int:booking_id>/mark-as-used", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_BOOKINGS)
def mark_booking_as_used(booking_id: int) -> utils.BackofficeResponse:
    booking = bookings_models.Booking.query.get_or_404(booking_id)
    if booking.status != bookings_models.BookingStatus.CANCELLED:
        flash("Impossible de valider une réservation qui n'est pas annulée", "warning")
        return _redirect_after_individual_booking_action()

    bookings_api.mark_as_used_with_uncancelling(booking)

    flash(f"La réservation {booking.token} a été validée", "success")
    return _redirect_after_individual_booking_action()


@individual_bookings_blueprint.route("/<int:booking_id>/cancel", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_BOOKINGS)
def mark_booking_as_cancelled(booking_id: int) -> utils.BackofficeResponse:
    booking = bookings_models.Booking.query.get_or_404(booking_id)

    try:
        bookings_api.mark_as_cancelled(booking)
    except bookings_exceptions.BookingIsAlreadyCancelled:
        flash("Impossible d'annuler une réservation déjà annulée", "warning")
    except bookings_exceptions.BookingIsAlreadyRefunded:
        flash("Impossible d'annuler une réservation remboursée", "warning")
    except bookings_exceptions.BookingIsAlreadyUsed:
        flash("Impossible d'annuler une réservation déjà utilisée", "warning")
    else:
        flash(f"La réservation {booking.token} a été annulée", "success")

    return _redirect_after_individual_booking_action()
