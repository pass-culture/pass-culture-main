import datetime
import typing
from io import BytesIO

import sqlalchemy.orm as sa_orm
from flask import flash
from flask import render_template
from flask import send_file
from flask_login import current_user
from markupsafe import Markup
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import NotFound

from pcapi import settings
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.api import booking as educational_api_booking
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.bookings import forms as booking_forms
from pcapi.routes.backoffice.bookings import helpers as booking_helpers
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.pro.utils import get_connect_as
from pcapi.utils import urls
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


collective_bookings_blueprint = utils.child_backoffice_blueprint(
    "collective_bookings",
    __name__,
    url_prefix="/collective-bookings",
    permission=perm_models.Permissions.READ_BOOKINGS,
)


def _get_collective_bookings_query() -> sa_orm.Query:
    return (
        db.session.query(educational_models.CollectiveBooking)
        .join(educational_models.CollectiveStock)
        .join(educational_models.CollectiveOffer)
        .join(educational_models.EducationalInstitution, educational_models.CollectiveBooking.educationalInstitution)
        .options(
            sa_orm.joinedload(educational_models.CollectiveBooking.collectiveStock)
            .load_only(
                educational_models.CollectiveStock.collectiveOfferId,
                educational_models.CollectiveStock.startDatetime,
                educational_models.CollectiveStock.endDatetime,
                educational_models.CollectiveStock.bookingLimitDatetime,
                # needed by total_amount:
                educational_models.CollectiveStock.price,
                educational_models.CollectiveStock.numberOfTickets,
            )
            .joinedload(educational_models.CollectiveStock.collectiveOffer)
            .load_only(
                educational_models.CollectiveOffer.id,
                educational_models.CollectiveOffer.name,
                educational_models.CollectiveOffer.formats,
            ),
            sa_orm.joinedload(educational_models.CollectiveBooking.educationalInstitution).load_only(
                educational_models.EducationalInstitution.id,
                educational_models.EducationalInstitution.name,
                educational_models.EducationalInstitution.institutionId,
                educational_models.EducationalInstitution.institutionType,
                educational_models.EducationalInstitution.city,
            ),
            sa_orm.joinedload(educational_models.CollectiveBooking.educationalRedactor).load_only(
                educational_models.EducationalRedactor.firstName, educational_models.EducationalRedactor.lastName
            ),
            sa_orm.joinedload(educational_models.CollectiveBooking.offerer).load_only(
                offerers_models.Offerer.id, offerers_models.Offerer.name
            ),
            sa_orm.joinedload(educational_models.CollectiveBooking.venue).load_only(
                # for name and link (build_pc_pro_venue_link)
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.isVirtual,
                offerers_models.Venue.managingOffererId,
            ),
            sa_orm.joinedload(educational_models.CollectiveBooking.pricings)
            .load_only(
                finance_models.Pricing.amount, finance_models.Pricing.status, finance_models.Pricing.creationDate
            )
            .joinedload(finance_models.Pricing.cashflows)
            .load_only(finance_models.Cashflow.batchId)
            .joinedload(finance_models.Cashflow.batch)
            .load_only(finance_models.CashflowBatch.label),
            sa_orm.joinedload(educational_models.CollectiveBooking.incidents)
            .joinedload(finance_models.BookingFinanceIncident.incident)
            .load_only(finance_models.FinanceIncident.id, finance_models.FinanceIncident.status),
        )
    )


def _get_collective_bookings(
    form: booking_forms.GetCollectiveBookingListForm,
) -> list[educational_models.CollectiveBooking]:
    base_query = _get_collective_bookings_query()

    if form.has_incident.data and len(form.has_incident.data) == 1:
        if form.has_incident.data[0] == "true":
            base_query = base_query.filter(educational_models.CollectiveBooking.validated_incident_id != None)
        else:
            base_query = base_query.filter(educational_models.CollectiveBooking.validated_incident_id == None)

    return booking_helpers.get_bookings(
        base_query=base_query,
        form=form,
        stock_class=educational_models.CollectiveStock,
        booking_class=educational_models.CollectiveBooking,
        offer_class=educational_models.CollectiveOffer,
        id_filters=[
            educational_models.CollectiveBooking.id,
            educational_models.CollectiveOffer.id,
        ],
        name_filters=[
            educational_models.CollectiveOffer.name,
        ],
    )


def _render_collective_bookings(collective_bookings_ids: list[int] | None = None) -> utils.BackofficeResponse:
    bookings: list[educational_models.CollectiveBooking] = []

    if collective_bookings_ids:
        query = _get_collective_bookings_query()
        bookings = query.filter(educational_models.CollectiveBooking.id.in_(collective_bookings_ids)).all()

    connect_as = {}
    for booking in bookings:
        offer = booking.collectiveStock.collectiveOffer
        connect_as[offer.id] = get_connect_as(
            object_type="collective_offer",
            object_id=offer.id,
            pc_pro_path=urls.build_pc_pro_offer_path(offer),
        )

    return render_template(
        "collective_bookings/rows.html",
        rows=bookings,
        mark_as_used_booking_form=empty_forms.EmptyForm(),
        cancel_booking_form=booking_forms.CancelCollectiveBookingForm(),
        connect_as=connect_as,
    )


@collective_bookings_blueprint.route("", methods=["GET"])
def list_collective_bookings() -> utils.BackofficeResponse:
    form = booking_forms.GetCollectiveBookingListForm(formdata=utils.get_query_params())
    if not form.validate():
        return render_template("collective_bookings/list.html", isEAC=True, rows=[], form=form), 400

    if form.is_empty():
        # Empty results when no filter is set
        return render_template("collective_bookings/list.html", rows=[], form=form)

    bookings = _get_collective_bookings(form)

    pro_visualisation_link = f"{settings.PRO_URL}/collective/bookings{form.pro_view_args}" if form.pro_view_args else ""

    bookings = utils.limit_rows(
        bookings,
        form.limit.data,
        sort_key=lambda booking: booking.collectiveStock.startDatetime,
        sort_reverse=True,
    )

    autocomplete.prefill_offerers_choices(form.offerer)
    autocomplete.prefill_venues_choices(form.venue)
    autocomplete.prefill_institutions_choices(form.institution)
    autocomplete.prefill_cashflow_batch_choices(form.cashflow_batches)

    connect_as = {}

    for booking in bookings:
        offer = booking.collectiveStock.collectiveOffer
        connect_as[offer.id] = get_connect_as(
            object_type="collective_offer",
            object_id=offer.id,
            pc_pro_path=urls.build_pc_pro_offer_path(offer),
        )

    return render_template(
        "collective_bookings/list.html",
        rows=bookings,
        form=form,
        mark_as_used_booking_form=empty_forms.EmptyForm(),
        cancel_booking_form=booking_forms.CancelCollectiveBookingForm(),
        pro_visualisation_link=pro_visualisation_link,
        connect_as=connect_as,
    )


@collective_bookings_blueprint.route("/download-csv", methods=["GET"])
def get_collective_booking_csv_download() -> utils.BackofficeResponse:
    form = booking_forms.GetDownloadBookingsForm(formdata=utils.get_query_params())
    if not form.validate():
        raise BadRequest()

    export_data = educational_api_booking.get_collective_booking_report(
        user=current_user,
        booking_period=typing.cast(tuple[datetime.date, datetime.date], form.from_to_date.data),
        venue_id=form.venue.data,
        export_type=bookings_models.BookingExportType.CSV,
    )
    buffer = BytesIO(typing.cast(str, export_data).encode("utf-8-sig"))
    return send_file(buffer, as_attachment=True, download_name="reservations_pass_culture.csv", mimetype="text/csv")


@collective_bookings_blueprint.route("/download-xlsx", methods=["GET"])
def get_collective_booking_xlsx_download() -> utils.BackofficeResponse:
    form = booking_forms.GetDownloadBookingsForm(formdata=utils.get_query_params())
    if not form.validate():
        raise BadRequest()

    export_data = educational_api_booking.get_collective_booking_report(
        user=current_user,
        booking_period=typing.cast(tuple[datetime.date, datetime.date], form.from_to_date.data),
        venue_id=form.venue.data,
        export_type=bookings_models.BookingExportType.EXCEL,
    )
    buffer = BytesIO(typing.cast(bytes, export_data))
    return send_file(
        buffer,
        as_attachment=True,
        download_name="reservations_pass_culture.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@collective_bookings_blueprint.route("/<int:collective_booking_id>/mark-as-used", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_BOOKINGS)
def mark_booking_as_used(collective_booking_id: int) -> utils.BackofficeResponse:
    collective_booking = (
        db.session.query(educational_models.CollectiveBooking).filter_by(id=collective_booking_id).one_or_none()
    )
    if not collective_booking:
        raise NotFound()

    if collective_booking.status != educational_models.CollectiveBookingStatus.CANCELLED:
        flash("Impossible de valider une réservation qui n'est pas annulée", "warning")
        return _render_collective_bookings([collective_booking_id])

    try:
        educational_api_booking.uncancel_collective_booking(collective_booking)
    except Exception as exc:
        mark_transaction_as_invalid()
        flash(Markup("Une erreur s'est produite : {message}").format(message=str(exc)), "warning")
    else:
        flash(f"La réservation <b>{collective_booking.id}</b> a été validée", "success")

    return _render_collective_bookings([collective_booking_id])


@collective_bookings_blueprint.route("/<int:collective_booking_id>/cancel", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_BOOKINGS)
def mark_booking_as_cancelled(collective_booking_id: int) -> utils.BackofficeResponse:
    collective_booking = (
        db.session.query(educational_models.CollectiveBooking).filter_by(id=collective_booking_id).one_or_none()
    )
    if not collective_booking:
        raise NotFound()

    form = booking_forms.CancelCollectiveBookingForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _render_collective_bookings()

    try:
        educational_api_booking.cancel_collective_booking(
            collective_booking,
            educational_models.CollectiveBookingCancellationReasons(form.reason.data),
            _from="support",
            author_id=current_user.id,
        )
    except educational_exceptions.CollectiveBookingAlreadyCancelled:
        mark_transaction_as_invalid()
        flash("Impossible d'annuler une réservation déjà annulée", "warning")
    except educational_exceptions.BookingIsAlreadyRefunded:
        mark_transaction_as_invalid()
        flash("Cette réservation est en train d’être remboursée, il est impossible de l’invalider", "warning")
    except Exception as exc:
        mark_transaction_as_invalid()
        flash(Markup("Une erreur s'est produite : {message}").format(message=str(exc)), "warning")
    else:
        flash(f"La réservation <b>{collective_booking.id}</b> a été annulée", "success")

    return _render_collective_bookings([collective_booking_id])
