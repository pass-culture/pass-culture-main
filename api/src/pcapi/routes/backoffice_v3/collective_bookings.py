import datetime

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
import sqlalchemy as sa

from pcapi.core.categories import subcategories_v2
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.api import booking as educational_api_booking
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.utils import date as date_utils

from . import autocomplete
from . import utils
from .forms import collective_booking as collective_booking_forms
from .forms import empty as empty_forms


collective_bookings_blueprint = utils.child_backoffice_blueprint(
    "collective_bookings",
    __name__,
    url_prefix="/collective-bookings",
    permission=perm_models.Permissions.READ_BOOKINGS,
)


def _get_collective_bookings(
    form: collective_booking_forms.GetCollectiveBookingListForm,
) -> list[educational_models.CollectiveBooking]:
    base_query = (
        educational_models.CollectiveBooking.query.outerjoin(educational_models.CollectiveStock)
        .outerjoin(educational_models.CollectiveOffer)
        .outerjoin(
            educational_models.EducationalInstitution, educational_models.CollectiveBooking.educationalInstitution
        )
        .options(
            sa.orm.joinedload(educational_models.CollectiveBooking.collectiveStock)
            .load_only(
                educational_models.CollectiveStock.collectiveOfferId,
                educational_models.CollectiveStock.beginningDatetime,
                educational_models.CollectiveStock.bookingLimitDatetime,
                # needed by total_amount:
                educational_models.CollectiveStock.price,
                educational_models.CollectiveStock.numberOfTickets,
            )
            .joinedload(educational_models.CollectiveStock.collectiveOffer)
            .load_only(
                educational_models.CollectiveOffer.id,
                educational_models.CollectiveOffer.name,
                educational_models.CollectiveOffer.subcategoryId,
            ),
            sa.orm.joinedload(educational_models.CollectiveBooking.educationalInstitution).load_only(
                educational_models.EducationalInstitution.id, educational_models.EducationalInstitution.name
            ),
            sa.orm.joinedload(educational_models.CollectiveBooking.educationalRedactor).load_only(
                educational_models.EducationalRedactor.firstName, educational_models.EducationalRedactor.lastName
            ),
            sa.orm.joinedload(educational_models.CollectiveBooking.offerer).load_only(
                offerers_models.Offerer.id, offerers_models.Offerer.name
            ),
            sa.orm.joinedload(educational_models.CollectiveBooking.venue).load_only(
                # for name and link (build_pc_pro_venue_link)
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.isVirtual,
                offerers_models.Venue.managingOffererId,
            ),
            sa.orm.joinedload(educational_models.CollectiveBooking.pricings)
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
        base_query = base_query.filter(educational_models.CollectiveBooking.dateCreated >= from_datetime)

    if form.to_date.data:
        to_datetime = date_utils.date_to_localized_datetime(form.to_date.data, datetime.datetime.max.time())
        base_query = base_query.filter(educational_models.CollectiveBooking.dateCreated <= to_datetime)

    if form.event_from_date.data:
        event_from_datetime = date_utils.date_to_localized_datetime(
            form.event_from_date.data, datetime.datetime.min.time()
        )
        base_query = base_query.filter(educational_models.CollectiveStock.beginningDatetime >= event_from_datetime)

    if form.event_to_date.data:
        event_to_datetime = date_utils.date_to_localized_datetime(form.event_to_date.data, datetime.datetime.max.time())
        base_query = base_query.filter(educational_models.CollectiveStock.beginningDatetime <= event_to_datetime)

    if form.offerer.data:
        base_query = base_query.filter(educational_models.CollectiveBooking.offererId.in_(form.offerer.data))

    if form.venue.data:
        base_query = base_query.filter(educational_models.CollectiveBooking.venueId.in_(form.venue.data))

    if form.category.data:
        base_query = base_query.filter(
            educational_models.CollectiveOffer.subcategoryId.in_(
                subcategory.id
                for subcategory in subcategories_v2.ALL_SUBCATEGORIES
                if subcategory.category.id in form.category.data
            )
        )

    if form.status.data:
        base_query = base_query.filter(educational_models.CollectiveBooking.status.in_(form.status.data))

    if form.cashflow_batches.data:
        base_query = (
            base_query.join(finance_models.Pricing).join(finance_models.CashflowPricing).join(finance_models.Cashflow)
        )
        base_query = base_query.filter(finance_models.Cashflow.batchId.in_(form.cashflow_batches.data))

    if form.q.data:
        search_query = form.q.data

        if search_query.isnumeric():
            # Performance is really better than .filter(sa.or_(...)) when searching for an id in different tables
            query = base_query.filter(educational_models.CollectiveBooking.id == int(search_query)).union(
                base_query.filter(educational_models.CollectiveOffer.id == int(search_query)),
                base_query.filter(educational_models.EducationalInstitution.id == int(search_query)),
            )
        else:
            name = "%{}%".format(search_query)
            query = base_query.filter(
                educational_models.EducationalInstitution.name.ilike(name),
            ).union(base_query.filter(educational_models.CollectiveOffer.name.ilike(name)))
    else:
        query = base_query

    # +1 to check if there are more results than requested
    return query.limit(form.limit.data + 1).all()


@collective_bookings_blueprint.route("", methods=["GET"])
def list_collective_bookings() -> utils.BackofficeResponse:
    form = collective_booking_forms.GetCollectiveBookingListForm(formdata=utils.get_query_params())
    if not form.validate():
        return render_template("collective_bookings/list.html", isEAC=True, rows=[], form=form), 400

    if form.is_empty():
        # Empty results when no filter is set
        return render_template("collective_bookings/list.html", rows=[], form=form)

    bookings = _get_collective_bookings(form)

    if len(bookings) > form.limit.data:
        flash(
            f"Il y a plus de {form.limit.data} résultats dans la base de données, la liste ci-dessous n'en donne donc "
            "qu'une partie. Veuillez affiner les filtres de recherche.",
            "info",
        )
        bookings = bookings[: form.limit.data]

    autocomplete.prefill_offerers_choices(form.offerer)
    autocomplete.prefill_venues_choices(form.venue)
    autocomplete.prefill_cashflow_batch_choices(form.cashflow_batches)

    return render_template(
        "collective_bookings/list.html",
        rows=bookings,
        form=form,
        mark_as_used_booking_form=empty_forms.EmptyForm(),
        cancel_booking_form=empty_forms.EmptyForm(),
    )


def _redirect_after_collective_booking_action(code: int = 303) -> utils.BackofficeResponse:
    if request.referrer:
        return redirect(request.referrer, code)

    return redirect(url_for("backoffice_v3_web.collective_bookings.list_collective_bookings"), code)


@collective_bookings_blueprint.route("/<int:collective_booking_id>/mark-as-used", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_BOOKINGS)
def mark_booking_as_used(collective_booking_id: int) -> utils.BackofficeResponse:
    collective_booking = educational_models.CollectiveBooking.query.get_or_404(collective_booking_id)
    if collective_booking.status != educational_models.CollectiveBookingStatus.CANCELLED:
        flash("Impossible de valider une réservation qui n'est pas annulée", "warning")
        return _redirect_after_collective_booking_action()

    try:
        educational_api_booking.uncancel_collective_booking_by_id_from_support(collective_booking)
    except Exception as exc:  # pylint: disable=broad-except
        flash(f"Une erreur s'est produite : {str(exc)}", "warning")
    else:
        flash(f"La réservation {collective_booking.id} a été validée", "success")

    return _redirect_after_collective_booking_action()


@collective_bookings_blueprint.route("/<int:collective_booking_id>/cancel", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_BOOKINGS)
def mark_booking_as_cancelled(collective_booking_id: int) -> utils.BackofficeResponse:
    collective_booking = educational_models.CollectiveBooking.query.get_or_404(collective_booking_id)

    try:
        educational_api_booking.cancel_collective_booking_by_id_from_support(collective_booking)
    except educational_exceptions.CollectiveBookingAlreadyCancelled:
        flash("Impossible d'annuler une réservation déjà annulée", "warning")
    except educational_exceptions.BookingIsAlreadyRefunded:
        flash("Impossible d'annuler une réservation remboursée", "warning")
    except Exception as exc:  # pylint: disable=broad-except
        flash(f"Une erreur s'est produite : {str(exc)}", "warning")
    else:
        flash(f"La réservation {collective_booking.id} a été annulée", "success")

    return _redirect_after_collective_booking_action()
