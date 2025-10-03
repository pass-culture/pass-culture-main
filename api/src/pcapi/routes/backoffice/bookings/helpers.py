import datetime
import logging
import typing
from collections import defaultdict

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask import flash
from flask import url_for
from flask_login import current_user
from markupsafe import Markup

from pcapi.connectors import ems
from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import exceptions as bookings_exceptions
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.educational import models as educational_models
from pcapi.core.external_bookings.cds import exceptions as cds_exceptions
from pcapi.core.external_bookings.cgr import exceptions as cgr_exceptions
from pcapi.core.finance import models as finance_models
from pcapi.core.geography import models as geography_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.backoffice.bookings.forms import BaseBookingListForm
from pcapi.routes.backoffice.bookings.forms import BookingStatus
from pcapi.routes.backoffice.filters import pluralize
from pcapi.utils import date as date_utils
from pcapi.utils import email as email_utils
from pcapi.utils import string as string_utils
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


def get_bookings(
    *,
    base_query: sa_orm.Query,
    form: BaseBookingListForm,
    stock_class: type[educational_models.CollectiveStock | offers_models.Stock],
    booking_class: type[educational_models.CollectiveBooking | bookings_models.Booking],
    offer_class: type[educational_models.CollectiveOffer | offers_models.Offer],
    search_by_email: bool = False,
    id_filters: typing.Iterable[sa_orm.InstrumentedAttribute] = (),
    name_filters: typing.Iterable[sa_orm.InstrumentedAttribute] = (),
    or_filters: list | None = None,
) -> list[bookings_models.Booking] | list[educational_models.CollectiveBooking]:
    start_column = (
        stock_class.startDatetime
        if stock_class is educational_models.CollectiveStock
        else stock_class.beginningDatetime
    )

    if or_filters is None:
        or_filters = []

    if form.from_to_date.data:
        from_datetime = date_utils.date_to_localized_datetime(form.from_to_date.from_date, datetime.datetime.min.time())
        if from_datetime:
            base_query = base_query.filter(booking_class.dateCreated >= from_datetime)

        to_datetime = date_utils.date_to_localized_datetime(form.from_to_date.to_date, datetime.datetime.max.time())
        if to_datetime:
            base_query = base_query.filter(booking_class.dateCreated <= to_datetime)

    event_from_datetime = date_utils.date_to_localized_datetime(form.event_from_date.data, datetime.datetime.min.time())
    if event_from_datetime and start_column:
        base_query = base_query.filter(start_column >= event_from_datetime)

    event_to_datetime = date_utils.date_to_localized_datetime(form.event_to_date.data, datetime.datetime.max.time())
    if event_to_datetime and start_column:
        base_query = base_query.filter(start_column <= event_to_datetime)

    if form.offerer.data:
        base_query = base_query.filter(booking_class.offererId.in_(form.offerer.data))

    if form.venue.data:
        base_query = base_query.filter(booking_class.venueId.in_(form.venue.data))

    if getattr(offer_class, "subcategoryId", None) and hasattr(form, "category") and form.category.data:
        base_query = base_query.filter(
            offer_class.subcategoryId.in_(
                subcategory.id
                for subcategory in subcategories.ALL_SUBCATEGORIES
                if subcategory.category.id in form.category.data
            )
        )
    elif hasattr(offer_class, "formats") and hasattr(form, "formats") and form.formats.data:
        base_query = base_query.filter(
            offer_class.formats.overlap(sa.dialects.postgresql.array((fmt for fmt in form.formats.data)))
        )

    if getattr(offer_class, "institution", None) and hasattr(form, "institution") and form.institution.data:
        base_query = base_query.filter(booking_class.educationalInstitutionId.in_(form.institution.data))

    if form.status.data:
        if booking_class is bookings_models.Booking:
            status_filters = []
            status_in = []
            for status in form.status.data:
                if status == BookingStatus.CONFIRMED.name:
                    status_filters.append(
                        sa.and_(
                            booking_class.isConfirmed,
                            booking_class.status == BookingStatus.CONFIRMED.name,
                        )
                    )
                elif status == BookingStatus.BOOKED.name:
                    status_filters.append(
                        sa.and_(
                            ~booking_class.isConfirmed,  # type: ignore[operator]
                            booking_class.status == BookingStatus.CONFIRMED.name,
                        )
                    )
                else:
                    status_in.append(status)

            if status_in:
                status_filters.append(booking_class.status.in_(status_in))

            if len(status_filters) > 1:
                base_query = base_query.filter(sa.or_(*status_filters))
            else:
                base_query = base_query.filter(status_filters[0])
        else:
            base_query = base_query.filter(booking_class.status.in_(form.status.data))

    if form.cashflow_batches.data:
        base_query = (
            base_query.join(finance_models.Pricing).join(finance_models.CashflowPricing).join(finance_models.Cashflow)
        )
        base_query = base_query.filter(finance_models.Cashflow.batchId.in_(form.cashflow_batches.data))

    if hasattr(form, "cancellation_reason") and form.cancellation_reason.data:
        base_query = base_query.filter(booking_class.cancellationReason.in_(form.cancellation_reason.data))

    if form.q.data:
        search_query = form.q.data

        if string_utils.is_numeric(search_query) and id_filters:
            for id_filter in id_filters:
                or_filters.append(id_filter == int(search_query))
        elif search_by_email:
            sanitized_email = email_utils.sanitize_email(search_query)
            if email_utils.is_valid_email(sanitized_email):
                or_filters.append(users_models.User.email == sanitized_email)

        if not or_filters and name_filters:
            for name_filter in name_filters:
                or_filters.append(name_filter.ilike(f"%{search_query}%"))

        query = base_query.filter(or_filters[0])

        if len(or_filters) > 1:
            # Performance is really better than .filter(sa.or_(...)) when searching for an id in different tables
            query = query.union(*(base_query.filter(f) for f in or_filters[1:]))
    else:
        query = base_query

    return query.limit(form.limit.data + 1).all()


def batch_validate_bookings(bookings: list[bookings_models.Booking]) -> None:
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
            except Exception as exc:
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


def batch_cancel_bookings(
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
                except Exception as exception:
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
            except Exception as exc:
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


def get_booking_query_for_validation() -> sa_orm.Query:
    return (
        db.session.query(bookings_models.Booking)
        .options(sa_orm.joinedload(bookings_models.Booking.user).selectinload(users_models.User.achievements))
        .options(sa_orm.joinedload(bookings_models.Booking.stock).joinedload(offers_models.Stock.offer))
    )


def get_booking_query_for_cancelation() -> sa_orm.Query:
    return db.session.query(bookings_models.Booking).options(
        sa_orm.joinedload(bookings_models.Booking.stock)
        .load_only(offers_models.Stock.id)
        .joinedload(offers_models.Stock.offer)
        .load_only(offers_models.Offer.id)
        .joinedload(offers_models.Offer.offererAddress)
        .load_only(offerers_models.OffererAddress.label)
        .joinedload(offerers_models.OffererAddress.address)
        .load_only(geography_models.Address.street, geography_models.Address.postalCode, geography_models.Address.city)
    )
