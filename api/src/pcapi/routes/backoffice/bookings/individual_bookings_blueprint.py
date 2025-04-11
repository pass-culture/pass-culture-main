from collections import defaultdict
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
import sqlalchemy.orm as sa_orm
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import NotFound

from pcapi import settings
from pcapi.connectors import ems
from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import exceptions as bookings_exceptions
from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings import repository as booking_repository
from pcapi.core.external_bookings.cds import exceptions as cds_exceptions
from pcapi.core.external_bookings.cgr import exceptions as cgr_exceptions
from pcapi.core.finance import models as finance_models
from pcapi.core.geography import models as geography_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.repository import atomic
from pcapi.repository import mark_transaction_as_invalid
from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.bookings import forms as booking_forms
from pcapi.routes.backoffice.bookings import helpers as booking_helpers
from pcapi.routes.backoffice.filters import pluralize
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.pro.utils import get_connect_as
from pcapi.utils import urls


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
            sa_orm.joinedload(bookings_models.Booking.stock)
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
            sa_orm.joinedload(bookings_models.Booking.user).load_only(
                users_models.User.id,
                users_models.User.firstName,
                users_models.User.lastName,
                users_models.User.postalCode,
            ),
            sa_orm.joinedload(bookings_models.Booking.offerer).load_only(
                offerers_models.Offerer.id, offerers_models.Offerer.name
            ),
            sa_orm.joinedload(bookings_models.Booking.venue).load_only(
                # for name and link (build_pc_pro_venue_link)
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.isVirtual,
                offerers_models.Venue.managingOffererId,
            ),
            sa_orm.joinedload(bookings_models.Booking.pricings)
            .load_only(
                finance_models.Pricing.amount, finance_models.Pricing.status, finance_models.Pricing.creationDate
            )
            .joinedload(finance_models.Pricing.cashflows)
            .load_only(finance_models.Cashflow.batchId)
            .joinedload(finance_models.Cashflow.batch)
            .load_only(finance_models.CashflowBatch.label),
            sa_orm.joinedload(bookings_models.Booking.incidents)
            .joinedload(finance_models.BookingFinanceIncident.incident)
            .load_only(finance_models.FinanceIncident.id, finance_models.FinanceIncident.status),
            sa_orm.joinedload(bookings_models.Booking.deposit).load_only(finance_models.Deposit.expirationDate),
            sa_orm.joinedload(bookings_models.Booking.fraudulentBookingTag)
            .joinedload(bookings_models.FraudulentBookingTag.author)
            .load_only(
                users_models.User.id,
                users_models.User.firstName,
                users_models.User.lastName,
            ),
        )
    )

    if form.deposit.data and form.deposit.data != booking_forms.DEPOSIT_DEFAULT_VALUE:
        base_query = base_query.join(finance_models.Deposit, bookings_models.Booking.deposit)
        if form.deposit.data == "active":
            base_query = base_query.filter(finance_models.Deposit.expirationDate > sa.func.now())
        elif form.deposit.data == "expired":
            base_query = base_query.filter(finance_models.Deposit.expirationDate <= sa.func.now())

    if len(form.is_duo.data) == 1:
        base_query = base_query.filter(bookings_models.Booking.quantity == form.is_duo.data[0])

    if form.is_fraudulent.data and len(form.is_fraudulent.data) == 1:
        if form.is_fraudulent.data[0] == "true":
            base_query = base_query.filter(bookings_models.Booking.fraudulentBookingTag != None)
        else:
            base_query = base_query.filter(bookings_models.Booking.fraudulentBookingTag == None)

    if form.has_incident.data and len(form.has_incident.data) == 1:
        if form.has_incident.data[0] == "true":
            base_query = base_query.filter(bookings_models.Booking.validated_incident_id != None)
        else:
            base_query = base_query.filter(bookings_models.Booking.validated_incident_id == None)

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

    connect_as = {}

    for booking in bookings:
        offer = booking.stock.offer
        connect_as[booking.id] = get_connect_as(
            object_id=offer.id,
            object_type="offer",
            pc_pro_path=urls.build_pc_pro_offer_path(offer),
        )

    return render_template(
        "individual_bookings/list.html",
        rows=bookings,
        form=form,
        connect_as=connect_as,
        mark_as_used_booking_form=empty_forms.EmptyForm(),
        cancel_booking_form=booking_forms.CancelIndividualBookingForm(),
        pro_visualisation_link=pro_visualisation_link,
    )


def _redirect_after_individual_booking_action() -> utils.BackofficeResponse:
    if request.referrer:
        return redirect(request.referrer)

    return redirect(url_for("backoffice_web.individual_bookings.list_individual_bookings"), code=303)


@individual_bookings_blueprint.route("/download-csv", methods=["GET"])
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


def _get_booking_query_for_validation() -> sa_orm.Query:
    return bookings_models.Booking.query.options(
        sa_orm.joinedload(bookings_models.Booking.user).selectinload(users_models.User.achievements)
    ).options(sa_orm.joinedload(bookings_models.Booking.stock).joinedload(offers_models.Stock.offer))


@individual_bookings_blueprint.route("/<int:booking_id>/mark-as-used", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_BOOKINGS)
def mark_booking_as_used(booking_id: int) -> utils.BackofficeResponse:
    booking = _get_booking_query_for_validation().filter_by(id=booking_id).one_or_none()
    if not booking:
        raise NotFound()
    _batch_validate_bookings([booking])

    return _redirect_after_individual_booking_action()


@individual_bookings_blueprint.route("/<int:booking_id>/cancel", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_BOOKINGS)
def mark_booking_as_cancelled(booking_id: int) -> utils.BackofficeResponse:
    booking = (
        bookings_models.Booking.query.filter_by(id=booking_id)
        .options(
            sa_orm.joinedload(bookings_models.Booking.stock)
            .load_only(offers_models.Stock.id)
            .joinedload(offers_models.Stock.offer)
            .load_only(offers_models.Offer.id)
            .joinedload(offers_models.Offer.offererAddress)
            .load_only(offerers_models.OffererAddress.label)
            .joinedload(offerers_models.OffererAddress.address)
            .load_only(
                geography_models.Address.street, geography_models.Address.postalCode, geography_models.Address.city
            )
        )
        .one_or_none()
    )
    if not booking:
        raise NotFound()

    form = booking_forms.CancelIndividualBookingForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _redirect_after_individual_booking_action()

    _batch_cancel_bookings([booking], bookings_models.BookingCancellationReasons(form.reason.data))

    return _redirect_after_individual_booking_action()


@individual_bookings_blueprint.route("/batch-validate", methods=["GET"])
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
@utils.permission_required(perm_models.Permissions.MANAGE_BOOKINGS)
def batch_validate_individual_bookings() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _redirect_after_individual_booking_action()

    bookings = _get_booking_query_for_validation().filter(bookings_models.Booking.id.in_(form.object_ids_list)).all()
    _batch_validate_bookings(bookings)

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

    bookings = bookings_models.Booking.query.filter(bookings_models.Booking.id.in_(form.object_ids_list)).all()
    _batch_cancel_bookings(bookings, bookings_models.BookingCancellationReasons(form.reason.data))

    return _redirect_after_individual_booking_action()


def _batch_validate_bookings(bookings: list[bookings_models.Booking]) -> None:
    error_dict = defaultdict(list)
    success_count = 0

    for booking in bookings:
        with atomic():
            token = booking.token
            try:
                if booking.status == bookings_models.BookingStatus.CANCELLED:
                    bookings_api.mark_as_used_with_uncancelling(
                        booking, bookings_models.BookingValidationAuthorType.BACKOFFICE
                    )
                else:
                    bookings_api.mark_as_used(booking, bookings_models.BookingValidationAuthorType.BACKOFFICE)
                success_count += 1
            except (
                bookings_exceptions.BookingIsAlreadyUsed,
                bookings_exceptions.BookingIsAlreadyRefunded,
                bookings_exceptions.BookingDepositCreditExpired,
            ) as exc:
                error_dict[exc.__class__.__name__].append(token)
                mark_transaction_as_invalid()
            except sa.exc.InternalError as exc:
                if exc.orig and "tooManyBookings" in str(exc.orig):
                    error_dict["tooManyBookings"].append(token)
                elif exc.orig and "insufficientFunds" in str(exc.orig):
                    error_dict["insufficientFunds"].append(token)
                else:
                    flash(
                        Markup(
                            "Une erreur s'est produite pour la réservation (<a class='link-primary' href='{url}'>{token}</a>) : {message}"
                        ).format(
                            token=token,
                            url=url_for(
                                "backoffice_web.individual_bookings.list_individual_bookings",
                                q=token,
                            ),
                            message=str(exc) or exc.__class__.__name__,
                        ),
                        "warning",
                    )
                mark_transaction_as_invalid()
            except Exception as exc:  # pylint: disable=broad-except
                flash(
                    Markup(
                        "Une erreur s'est produite pour la réservation (<a class='link-primary' href='{url}'>{token}</a>) : {message}"
                    ).format(
                        token=token,
                        url=url_for(
                            "backoffice_web.individual_bookings.list_individual_bookings",
                            q=token,
                        ),
                        message=str(exc) or exc.__class__.__name__,
                    ),
                    "warning",
                )
                mark_transaction_as_invalid()

    _flash_success_and_error_messages(success_count, error_dict, True)


def _batch_cancel_bookings(
    bookings: list[bookings_models.Booking], reason: bookings_models.BookingCancellationReasons
) -> None:
    error_dict = defaultdict(list)
    success_count = 0

    for booking in bookings:
        with atomic():
            token = booking.token
            try:
                bookings_api.mark_as_cancelled(
                    booking=booking,
                    reason=reason,
                    author_id=current_user.id,
                )
                success_count += 1
            except (
                bookings_exceptions.BookingIsAlreadyUsed,
                bookings_exceptions.BookingIsAlreadyRefunded,
                bookings_exceptions.BookingIsAlreadyCancelled,
            ) as exc:
                error_dict[exc.__class__.__name__].append(token)
                mark_transaction_as_invalid()
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
                        booking=booking,
                        reason=reason,
                        one_side_cancellation=True,
                        author_id=current_user.id,
                    )
                    success_count += 1
                except Exception as exception:  # pylint: disable=broad-except
                    mark_transaction_as_invalid()
                    flash(
                        Markup(
                            "Une erreur s'est produite pour la réservation (<a class='link-primary' href='{url}'>{token}</a>) : {message}"
                        ).format(
                            token=token,
                            url=url_for(
                                "backoffice_web.individual_bookings.list_individual_bookings",
                                q=token,
                            ),
                            message=str(exception) or exception.__class__.__name__,
                        ),
                        "warning",
                    )
            except Exception as exc:  # pylint: disable=broad-except
                mark_transaction_as_invalid()
                flash(
                    Markup(
                        "Une erreur s'est produite pour la réservation (<a class='link-primary' href='{url}'>{token}</a>) : {message}"
                    ).format(
                        token=token,
                        url=url_for(
                            "backoffice_web.individual_bookings.list_individual_bookings",
                            q=token,
                        ),
                        message=str(exc) or exc.__class__.__name__,
                    ),
                    "warning",
                )

    _flash_success_and_error_messages(success_count, error_dict, False)


def _flash_success_and_error_messages(
    success_count: int, error_dict: dict[str, list[str]], is_validating: bool
) -> None:
    if success_count > 0:
        flash(
            f"{success_count} {pluralize(success_count, 'réservation a', 'réservations ont')} été {'validée' if is_validating else 'annulée'}{pluralize(success_count)}",
            "success",
        )

    if error_dict:
        if success_count > 0:
            error_text = Markup("Certaines réservations n'ont pas pu être {action} et ont été ignorées :<br> ").format(
                action="validées" if is_validating else "annulées"
            )
        else:
            error_text = Markup("Impossible {action} ces réservations : <br>").format(
                action="de valider" if is_validating else "d'annuler"
            )
        for key in error_dict:
            tokens = error_dict[key]
            match key:
                case "BookingIsAlreadyCancelled":
                    error_text += _build_booking_error_str(
                        tokens,
                        f"réservation{pluralize(len(tokens))} déjà annulée{pluralize(len(tokens))}",
                    )
                case "BookingIsAlreadyUsed":
                    error_text += _build_booking_error_str(
                        tokens,
                        f"réservation{pluralize(len(tokens))} déjà validée{pluralize(len(tokens))}",
                    )
                case "BookingIsAlreadyRefunded":
                    error_text += _build_booking_error_str(
                        tokens,
                        f"réservation{pluralize(len(tokens))} déjà remboursée{pluralize(len(tokens))}",
                    )
                case "BookingDepositCreditExpired":
                    error_text += _build_booking_error_str(
                        tokens,
                        f"réservation{pluralize(len(tokens))} dont le crédit associé est expiré",
                    )
                case "tooManyBookings":
                    error_text += _build_booking_error_str(
                        tokens,
                        f"réservation{pluralize(len(tokens))} dont l'offre n'a plus assez de stock disponible",
                    )
                case "insufficientFunds":
                    error_text += _build_booking_error_str(
                        tokens,
                        f"réservation{pluralize(len(tokens))} dont le crédit associé est insuffisant",
                    )
        flash(error_text, "warning")


def _build_booking_error_str(tokens: list[str], message: str) -> str:
    return Markup("- {count} {message} (<a class='link-primary' href='{url}'>{tokens}</a>)<br>").format(
        count=len(tokens),
        message=message,
        url=url_for(
            "backoffice_web.individual_bookings.list_individual_bookings",
            q=", ".join(tokens),
        ),
        tokens=", ".join(tokens),
    )
