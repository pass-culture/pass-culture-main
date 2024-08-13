import datetime
from io import BytesIO
import logging
import re
import typing

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import send_file
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
import sqlalchemy as sa
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import NotFound

from pcapi import repository
from pcapi import settings
from pcapi.connectors import ems
from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import exceptions as bookings_exceptions
from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings import repository as booking_repository
from pcapi.core.external_bookings.cds import exceptions as cds_exceptions
from pcapi.core.external_bookings.cgr import exceptions as cgr_exceptions
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.bookings import forms as booking_forms
from pcapi.routes.backoffice.bookings import helpers as booking_helpers
from pcapi.routes.backoffice.forms import empty as empty_forms


logger = logging.getLogger(__name__)

individual_bookings_blueprint = utils.child_backoffice_blueprint(
    "individual_bookings",
    __name__,
    url_prefix="/individual-bookings",
    permission=perm_models.Permissions.READ_BOOKINGS,
)


BOOKING_TOKEN_RE = re.compile(r"^[A-Za-z0-9]{6}$")
NO_DIGIT_RE = re.compile(r"[^\d]+$")


def _get_individual_bookings(
    form: booking_forms.GetIndividualBookingListForm,
) -> list[bookings_models.Booking]:
    base_query = (
        bookings_models.Booking.query.join(offers_models.Stock)
        .join(offers_models.Offer)
        .join(users_models.User, bookings_models.Booking.user)
        .options(
            sa.orm.joinedload(bookings_models.Booking.stock)
            .load_only(
                offers_models.Stock.quantity,
                offers_models.Stock.offerId,
                offers_models.Stock.beginningDatetime,
                offers_models.Stock.bookingLimitDatetime,
            )
            .joinedload(offers_models.Stock.offer)
            .load_only(
                offers_models.Offer.id,
                offers_models.Offer.name,
                offers_models.Offer.isDuo,
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
                offerers_models.Venue.publicName,
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
            sa.orm.joinedload(bookings_models.Booking.incidents)
            .joinedload(finance_models.BookingFinanceIncident.incident)
            .load_only(finance_models.FinanceIncident.id, finance_models.FinanceIncident.status),
        )
    )

    if form.deposit.data and form.deposit.data != booking_forms.DEPOSIT_DEFAULT_VALUE:
        base_query = base_query.join(finance_models.Deposit, bookings_models.Booking.deposit).options(
            sa.orm.contains_eager(bookings_models.Booking.deposit).load_only(
                finance_models.Deposit.expirationDate,
            )
        )
        if form.deposit.data == "active":
            base_query = base_query.filter(finance_models.Deposit.expirationDate > sa.func.now())
        elif form.deposit.data == "expired":
            base_query = base_query.filter(finance_models.Deposit.expirationDate <= sa.func.now())
    else:
        base_query = base_query.options(
            sa.orm.joinedload(bookings_models.Booking.deposit).load_only(finance_models.Deposit.expirationDate),
        )

    or_filters = []
    if form.q.data:
        search_query = form.q.data

        terms = search_utils.split_terms(search_query)
        if all(BOOKING_TOKEN_RE.match(term) for term in terms):
            or_filters += [bookings_models.Booking.token == term.upper() for term in terms]

            if all(NO_DIGIT_RE.match(term) for term in terms):
                flash(
                    Markup(
                        "Le critère de recherche « {search_query} » peut correspondre à un nom. Cependant, la recherche "
                        "n'a porté que sur les codes contremarques afin de répondre rapidement. Veuillez inclure prénom et "
                        "nom dans le cas d'un nom de 6 lettres."
                    ).format(search_query=search_query),
                    "info",
                )

    return booking_helpers.get_bookings(
        base_query=base_query,
        form=form,
        stock_class=offers_models.Stock,
        booking_class=bookings_models.Booking,
        offer_class=offers_models.Offer,
        search_by_email=True,
        id_filters=[
            bookings_models.Booking.id,
            offers_models.Offer.id,
            users_models.User.id,
        ],
        name_filters=[
            offers_models.Offer.name,
        ],
        or_filters=or_filters,
    )


@individual_bookings_blueprint.route("", methods=["GET"])
@repository.atomic()
def list_individual_bookings() -> utils.BackofficeResponse:
    form = booking_forms.GetIndividualBookingListForm(formdata=utils.get_query_params())
    if not form.validate():
        return render_template("individual_bookings/list.html", rows=[], form=form), 400

    if form.is_empty():
        # Empty results when no filter is set
        return render_template("individual_bookings/list.html", rows=[], form=form)

    bookings = _get_individual_bookings(form)

    pro_visualisation_link = f"{settings.PRO_URL}/reservations{form.pro_view_args}" if form.pro_view_args else ""

    bookings = utils.limit_rows(
        bookings,
        form.limit.data,
        sort_key=lambda booking: (
            (booking.stock.beginningDatetime or booking.dateUsed or datetime.datetime.max),
            booking.dateCreated,
        ),
        sort_reverse=True,
    )

    autocomplete.prefill_offerers_choices(form.offerer)
    autocomplete.prefill_venues_choices(form.venue)
    autocomplete.prefill_cashflow_batch_choices(form.cashflow_batches)

    return render_template(
        "individual_bookings/list.html",
        rows=bookings,
        form=form,
        mark_as_used_booking_form=empty_forms.EmptyForm(),
        cancel_booking_form=booking_forms.CancelIndividualBookingForm(),
        pro_visualisation_link=pro_visualisation_link,
    )


def _redirect_after_individual_booking_action() -> utils.BackofficeResponse:
    if request.referrer:
        return redirect(request.referrer)

    return redirect(url_for("backoffice_web.individual_bookings.list_individual_bookings"), code=303)


@individual_bookings_blueprint.route("/download-csv", methods=["GET"])
@repository.atomic()
def get_individual_booking_csv_download() -> utils.BackofficeResponse:
    form = booking_forms.GetDownloadBookingsForm(formdata=utils.get_query_params())
    if not form.validate():
        raise BadRequest()

    export_data = booking_repository.get_export(
        user=current_user,
        booking_period=typing.cast(tuple[datetime.date, datetime.date], form.from_to_date.data),
        venue_id=form.venue.data,
        export_type=bookings_models.BookingExportType.CSV,
    )
    buffer = BytesIO(typing.cast(str, export_data).encode("utf-8-sig"))
    return send_file(buffer, as_attachment=True, download_name="reservations_pass_culture.csv", mimetype="text/csv")


@individual_bookings_blueprint.route("/download-xlsx", methods=["GET"])
@repository.atomic()
def get_individual_booking_xlsx_download() -> utils.BackofficeResponse:
    form = booking_forms.GetDownloadBookingsForm(formdata=utils.get_query_params())
    if not form.validate():
        raise BadRequest()

    export_data = booking_repository.get_export(
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


@individual_bookings_blueprint.route("/<int:booking_id>/mark-as-used", methods=["POST"])
@repository.atomic()
@utils.permission_required(perm_models.Permissions.MANAGE_BOOKINGS)
def mark_booking_as_used(booking_id: int) -> utils.BackofficeResponse:
    booking = bookings_models.Booking.query.filter_by(id=booking_id).one_or_none()
    if not booking:
        raise NotFound()

    if booking.status != bookings_models.BookingStatus.CANCELLED:
        flash("Impossible de valider une réservation qui n'est pas annulée", "warning")
        return _redirect_after_individual_booking_action()

    try:
        bookings_api.mark_as_used_with_uncancelling(booking, bookings_models.BookingValidationAuthorType.BACKOFFICE)
    except bookings_exceptions.BookingDepositCreditExpired:
        repository.mark_transaction_as_invalid()
        flash(
            Markup("La réservation <b>{token}</b> ne peut être validée, car le crédit associé est expiré.").format(
                token=booking.token
            ),
            "warning",
        )
    except sa.exc.InternalError as exc:
        repository.mark_transaction_as_invalid()
        if exc.orig and "tooManyBookings" in str(exc.orig):
            flash(
                "Impossible de valider une réservation dont le stock est épuisé",
                "warning",
            )
        elif exc.orig and "insufficientFunds" in str(exc.orig):
            flash(
                "Impossible de valider une réservation dont le crédit du jeune est épuisé",
                "warning",
            )
        else:
            flash(Markup("Une erreur s'est produite : {message}").format(message=str(exc)), "warning")
    except Exception as exc:  # pylint: disable=broad-except
        repository.mark_transaction_as_invalid()
        flash(Markup("Une erreur s'est produite : {message}").format(message=str(exc)), "warning")
    else:
        flash(Markup("La réservation <b>{token}</b> a été validée").format(token=booking.token), "success")

    return _redirect_after_individual_booking_action()


@individual_bookings_blueprint.route("/<int:booking_id>/cancel", methods=["POST"])
@repository.atomic()
@utils.permission_required(perm_models.Permissions.MANAGE_BOOKINGS)
def mark_booking_as_cancelled(booking_id: int) -> utils.BackofficeResponse:
    booking = bookings_models.Booking.query.filter_by(id=booking_id).one_or_none()
    if not booking:
        raise NotFound()

    form = booking_forms.CancelIndividualBookingForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _redirect_after_individual_booking_action()

    try:
        bookings_api.mark_as_cancelled(booking, bookings_models.BookingCancellationReasons(form.reason.data))
    except bookings_exceptions.BookingIsAlreadyCancelled:
        repository.mark_transaction_as_invalid()
        flash("Impossible d'annuler une réservation déjà annulée", "warning")
    except bookings_exceptions.BookingIsAlreadyRefunded:
        # The same exception is issued when Pricing is PROCESSED or when INVOICED with Payment
        repository.mark_transaction_as_invalid()
        flash("Cette réservation est en train d’être remboursée, il est impossible de l’invalider", "warning")
    except bookings_exceptions.BookingIsAlreadyUsed:
        repository.mark_transaction_as_invalid()
        flash("Impossible d'annuler une réservation déjà utilisée", "warning")
    except (
        cgr_exceptions.CGRAPIException,
        cds_exceptions.CineDigitalServiceAPIException,
        ems.EMSAPIException,
    ) as exc:
        logger.info(
            "API error for cancelling external booking, the booking will be cancelled unilaterally",
            extra={"booking_id": booking.id, "exc": str(exc)},
        )
        try:
            bookings_api.mark_as_cancelled(
                booking, bookings_models.BookingCancellationReasons(form.reason.data), one_side_cancellation=True
            )
        except Exception as exception:  # pylint: disable=broad-except
            repository.mark_transaction_as_invalid()
            flash(Markup("Une erreur s'est produite : {message}").format(message=str(exception)), "warning")
        else:
            flash(Markup("La réservation <b>{token}</b> a été annulée").format(token=booking.token), "success")
    except Exception as exc:  # pylint: disable=broad-except
        repository.mark_transaction_as_invalid()
        flash(Markup("Une erreur s'est produite : {message}").format(message=str(exc)), "warning")
    else:
        flash(Markup("La réservation <b>{token}</b> a été annulée").format(token=booking.token), "success")

    return _redirect_after_individual_booking_action()


@individual_bookings_blueprint.route("/batch-validate", methods=["GET"])
@repository.atomic()
@utils.permission_required(perm_models.Permissions.MANAGE_BOOKINGS)
def get_batch_validate_individual_bookings_form() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.individual_bookings.batch_validate_individual_bookings"),
        div_id="batch-validate-booking-modal",
        title="Voulez-vous vraiment valider les réservations ?",
        button_text="Valider les réservations",
    )


@individual_bookings_blueprint.route("/batch-validate", methods=["POST"])
@repository.atomic()
@utils.permission_required(perm_models.Permissions.MANAGE_BOOKINGS)
def batch_validate_individual_bookings() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _redirect_after_individual_booking_action()

    def _booking_callback(booking: bookings_models.Booking) -> None:
        try:
            bookings_api.mark_as_used(booking, bookings_models.BookingValidationAuthorType.BACKOFFICE)
        except bookings_exceptions.BookingIsAlreadyCancelled:
            bookings_api.mark_as_used_with_uncancelling(booking, bookings_models.BookingValidationAuthorType.BACKOFFICE)

    try:
        return _batch_individual_bookings_action(form, _booking_callback, "Les réservations ont été validées")
    except sa.exc.InternalError as exc:
        if exc.orig and "tooManyBookings" in str(exc.orig):
            flash("Pas assez de stock disponible pour cette offre", "warning")
        elif exc.orig and "insufficientFunds" in str(exc.orig):
            flash(
                "Le solde d'au moins un des comptes jeune est insuffisant pour valider ces réservations",
                "warning",
            )
        else:
            raise exc
    repository.mark_transaction_as_invalid()
    return _redirect_after_individual_booking_action()


@individual_bookings_blueprint.route("/batch-cancel", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_BOOKINGS)
def get_batch_cancel_individual_bookings_form() -> utils.BackofficeResponse:
    form = booking_forms.BatchCancelIndividualBookingsForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.individual_bookings.batch_cancel_individual_bookings"),
        div_id="batch-cancel-booking-modal",
        title="Annuler les réservations",
        button_text="Annuler les réservations",
    )


@individual_bookings_blueprint.route("/batch-cancel", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_BOOKINGS)
def batch_cancel_individual_bookings() -> utils.BackofficeResponse:
    form = booking_forms.BatchCancelIndividualBookingsForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _redirect_after_individual_booking_action()

    return _batch_individual_bookings_action(
        form,
        lambda booking: bookings_api.mark_as_cancelled(
            booking, bookings_models.BookingCancellationReasons(form.reason.data)
        ),
        "Les réservations ont été annulées",
    )


def _batch_individual_bookings_action(
    form: empty_forms.BatchForm, booking_callback: typing.Callable, success_message: str
) -> utils.BackofficeResponse:
    bookings = bookings_models.Booking.query.filter(bookings_models.Booking.id.in_(form.object_ids_list)).all()
    one_or_more_booking_passed = False

    for booking in bookings:
        try:
            booking_callback(booking)
            one_or_more_booking_passed = True
        except bookings_exceptions.BookingIsAlreadyCancelled:
            flash("Au moins une des réservations a déjà été annulée", "warning")
            return _redirect_after_individual_booking_action()
        except bookings_exceptions.BookingIsAlreadyUsed:
            flash("Au moins une des réservations a déjà été validée", "warning")
            return _redirect_after_individual_booking_action()
        except bookings_exceptions.BookingIsAlreadyRefunded:
            flash("Au moins une des réservations a déjà été remboursée", "warning")
            return _redirect_after_individual_booking_action()
        except bookings_exceptions.BookingDepositCreditExpired:
            flash(
                f"La réservation <b>{booking.token}</b> ne peut être validée, car le crédit associé est expiré.",
                "warning",
            )
            if not one_or_more_booking_passed:
                return _redirect_after_individual_booking_action()

    if one_or_more_booking_passed:
        flash(success_message, "success")

    return _redirect_after_individual_booking_action()
