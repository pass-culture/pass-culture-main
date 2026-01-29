import datetime
import json
import logging
import typing
from functools import partial
from itertools import groupby
from operator import attrgetter

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask import current_app
from sqlalchemy.sql.base import ExecutableOption

import pcapi.core.external_bookings.api as external_bookings_api
import pcapi.core.external_bookings.exceptions as external_bookings_exceptions
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.exceptions as finance_exceptions
import pcapi.core.finance.models as finance_models
import pcapi.core.finance.repository as finance_repository
import pcapi.core.geography.models as geography_models
import pcapi.core.mails.transactional as transactional_mails
import pcapi.core.offers.api as offers_api
import pcapi.core.offers.exceptions as offers_exceptions
import pcapi.core.offers.models as offers_models
import pcapi.core.offers.validation as offers_validation
import pcapi.core.providers.repository as providers_repository
import pcapi.serialization.utils as serialization_utils
from pcapi.connectors.ems import EMSAPIException
from pcapi.core import search
from pcapi.core.achievements import api as achievements_api
from pcapi.core.categories.subcategories import NUMBER_SECONDS_HIDE_QR_CODE
from pcapi.core.categories.subcategories import SEANCE_CINE
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import utils as educational_utils
from pcapi.core.external import batch
from pcapi.core.external.attributes.api import update_external_pro
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.external.batch import track_offer_booked_event
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import repository as offers_repository
from pcapi.core.providers.clients.ems_client import EMS_EXTERNAL_BOOKINGS_TO_CANCEL
from pcapi.core.providers.clients.ems_client import EMSAPIClient
from pcapi.core.search.models import IndexationReason
from pcapi.core.users import constants as users_constants
from pcapi.core.users import models as users_models
from pcapi.core.users.repository import get_and_lock_user
from pcapi.core.users.utils import get_age_at_date
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.tasks.serialization.external_api_booking_notification_tasks import BookingAction
from pcapi.utils import date as date_utils
from pcapi.utils import queue
from pcapi.utils import repository as pcapi_repository
from pcapi.utils.repository import transaction
from pcapi.utils.requests import exceptions as requests_exceptions
from pcapi.utils.transaction_manager import is_managed_transaction
from pcapi.utils.transaction_manager import mark_transaction_as_invalid
from pcapi.utils.transaction_manager import on_commit
from pcapi.workers import apps_flyer_job
from pcapi.workers import push_notification_job

from . import constants
from . import exceptions
from . import models
from . import repository
from . import utils
from . import validation


logger = logging.getLogger(__name__)


def _is_ended_booking(booking: models.Booking) -> bool:
    if (
        booking.stock.beginningDatetime
        and booking.status != models.BookingStatus.CANCELLED
        and booking.stock.beginningDatetime >= date_utils.get_naive_utc_now()
    ):
        # consider future events as "ongoing" even if they are used
        return False

    if (booking.stock.canHaveActivationCodes and booking.activationCode) or booking.display_even_if_used:
        # consider digital bookings and free offer from defined subcategories as special: is_used should be true anyway so
        # let's use displayAsEnded
        return bool(booking.displayAsEnded)

    return (
        not booking.stock.offer.isPermanent
        if booking.is_used_or_reimbursed
        else booking.status == models.BookingStatus.CANCELLED
    )


def is_booking_by_18_user(booking: models.Booking) -> bool:
    if not booking.deposit or not booking.user.birth_date:
        return False
    if booking.deposit.type == finance_models.DepositType.GRANT_18:
        return True
    if booking.deposit.type == finance_models.DepositType.GRANT_17_18:
        return get_age_at_date(booking.user.birth_date, booking.dateCreated, booking.user.departementCode) >= 18
    return False


def _get_booking_options() -> list[ExecutableOption]:
    return [
        sa_orm.joinedload(models.Booking.stock)
        .load_only(
            offers_models.Stock.id,
            offers_models.Stock.beginningDatetime,
            offers_models.Stock.price,
            offers_models.Stock.features,
            offers_models.Stock.offerId,
        )
        .options(
            sa_orm.joinedload(offers_models.Stock.offer)
            .load_only(
                offers_models.Offer.bookingContact,
                offers_models.Offer.name,
                offers_models.Offer.url,
                offers_models.Offer.subcategoryId,
                offers_models.Offer.withdrawalDetails,
                offers_models.Offer.withdrawalType,
                offers_models.Offer.withdrawalDelay,
                offers_models.Offer._extraData,
            )
            .options(
                sa_orm.joinedload(offers_models.Offer.product)
                .load_only(
                    offers_models.Product.id,
                    offers_models.Product.thumbCount,
                )
                .joinedload(offers_models.Product.productMediations),
                sa_orm.joinedload(offers_models.Offer.venue)
                .load_only(
                    offerers_models.Venue.name,
                    offerers_models.Venue.publicName,
                    offerers_models.Venue._bannerUrl,
                    offerers_models.Venue.isOpenToPublic,
                    offerers_models.Venue.venueTypeCode,
                )
                .options(
                    sa_orm.joinedload(offerers_models.Venue.offererAddress).joinedload(
                        offerers_models.OffererAddress.address
                    ),
                    sa_orm.joinedload(offerers_models.Venue.googlePlacesInfo),
                ),
                sa_orm.joinedload(offers_models.Offer.mediations),
                sa_orm.joinedload(offers_models.Offer.offererAddress)
                .load_only(offerers_models.OffererAddress.addressId, offerers_models.OffererAddress.label)
                .joinedload(offerers_models.OffererAddress.address),
            ),
            sa_orm.joinedload(offers_models.Stock.priceCategory)
            .joinedload(offers_models.PriceCategory.priceCategoryLabel)
            .load_only(offers_models.PriceCategoryLabel.label),
        ),
        sa_orm.joinedload(models.Booking.activationCode),
        sa_orm.joinedload(models.Booking.externalBookings),
        sa_orm.joinedload(models.Booking.deposit).load_only(finance_models.Deposit.type),
        sa_orm.joinedload(models.Booking.user).joinedload(users_models.User.reactions),
    ]


def get_booking_by_id(user: users_models.User, booking_id: int) -> models.Booking | None:
    """
    Get a booking by id for a user, with all the data needed for the bookings page
    including the offer and venue data.
    """
    return (
        db.session.query(models.Booking)
        .filter_by(userId=user.id, id=booking_id)
        .options(*_get_booking_options())
        .one_or_none()
    )


def get_individual_bookings(user: users_models.User) -> list[models.Booking]:
    """
    Get all bookings for a user, with all the data needed for the bookings page
    including the offer and venue data.
    """
    return (db.session.query(models.Booking).filter_by(userId=user.id).options(*_get_booking_options())).all()


def classify_and_sort_bookings(
    individual_bookings: list[models.Booking],
) -> tuple[list[models.Booking], list[models.Booking]]:
    """
    Classify bookings between ended and ongoing bookings
    """
    ended_bookings = []
    ongoing_bookings = []
    for booking in individual_bookings:
        if _is_ended_booking(booking):
            ended_bookings.append(booking)
        else:
            ongoing_bookings.append(booking)
            booking.qrCodeData = utils.get_qr_code_data(booking.token)

    sorted_ended_bookings = sorted(
        ended_bookings,
        key=lambda b: b.stock.beginningDatetime or b.dateUsed or b.cancellationDate or datetime.datetime.min,
        reverse=True,
    )
    # put permanent bookings at the end with datetime.max
    sorted_ongoing_bookings = sorted(
        ongoing_bookings,
        key=lambda b: (
            b.expirationDate or b.stock.beginningDatetime or datetime.datetime.max,
            -b.id,
        ),
    )
    return (sorted_ended_bookings, sorted_ongoing_bookings)


def get_user_bookings_by_status(user: users_models.User, status: str) -> list[models.Booking]:
    """
    Get 'ended' or 'ongoing' bookings for a user, with only the data needed for the booking page.
    """
    query = (
        db.session.query(models.Booking)
        .filter_by(userId=user.id)
        .options(
            sa_orm.load_only(
                models.Booking.amount,
                models.Booking.cancellationDate,
                models.Booking.cancellationReason,
                models.Booking.dateCreated,
                models.Booking.dateUsed,
                models.Booking.displayAsEnded,
                models.Booking.quantity,
                models.Booking.status,
            ),
            sa_orm.joinedload(models.Booking.activationCode).load_only(
                offers_models.ActivationCode.code,
                offers_models.ActivationCode.expirationDate,
            ),
            sa_orm.joinedload(models.Booking.stock)
            .load_only(
                offers_models.Stock.id,
                offers_models.Stock.beginningDatetime,
                offers_models.Stock.offerId,
                offers_models.Stock.price,
            )
            .joinedload(offers_models.Stock.offer)
            .load_only(
                offers_models.Offer.name,
                offers_models.Offer.subcategoryId,
                offers_models.Offer.withdrawalDelay,
                offers_models.Offer.withdrawalType,
                offers_models.Offer.isDuo,
                offers_models.Offer.canExpire,
            )
            .options(
                sa_orm.joinedload(offers_models.Offer.product),
                sa_orm.joinedload(offers_models.Offer.venue)
                .load_only(offerers_models.Venue.name)
                .joinedload(offerers_models.Venue.offererAddress)
                .load_only(offerers_models.OffererAddress.label)
                .joinedload(offerers_models.OffererAddress.address)
                .load_only(geography_models.Address.timezone),
                sa_orm.joinedload(offers_models.Offer.mediations),
            )
            .options(
                sa_orm.joinedload(offers_models.Offer.offererAddress)
                .load_only(offerers_models.OffererAddress.label)
                .joinedload(offerers_models.OffererAddress.address)
                .load_only(geography_models.Address.timezone, geography_models.Address.city),
            ),
            sa_orm.joinedload(models.Booking.user).joinedload(users_models.User.reactions),
        )
    )

    query_filter = sa.or_(
        models.Booking.displayAsEnded.is_(True),
        models.Booking.status.in_(
            [models.BookingStatus.USED, models.BookingStatus.REIMBURSED, models.BookingStatus.CANCELLED]
        ),
    )

    if status == models.BookingsListStatus.ENDED.value:
        return query.filter(query_filter).all()
    return query.filter(sa.not_(query_filter)).all()


def _book_offer(
    beneficiary: users_models.User,
    stock_id: int,
    quantity: int,
) -> models.Booking:
    """
    Return a booking or raise an exception if it's not possible.
    Update a user's credit information on Batch.
    """
    # The call to transaction here ensures we free the FOR UPDATE lock
    # on the stock if validation issues an exception
    with transaction():
        stock = offers_repository.get_and_lock_stock(stock_id=stock_id)
        get_and_lock_user(beneficiary.id)
        validation.check_offer_category_is_bookable_by_user(beneficiary, stock)
        validation.check_can_book_free_offer(beneficiary, stock)
        validation.check_offer_already_booked(beneficiary, stock.offer)
        validation.check_quantity(stock.offer, quantity)
        validation.check_stock_is_bookable(stock, quantity)
        total_amount = quantity * stock.price
        validation.check_expenses_limits(beneficiary, total_amount, stock.offer)

        is_activation_code_applicable = (
            stock.canHaveActivationCodes
            and db.session.query(
                db.session.query(offers_models.ActivationCode).filter_by(stock=stock).exists()
            ).scalar()
        )
        if is_activation_code_applicable:
            validation.check_activation_code_available(stock)

        booking = models.Booking(
            userId=beneficiary.id,
            stockId=stock.id,
            amount=stock.price,
            quantity=quantity,
            token=repository.generate_booking_token(),
            venueId=stock.offer.venueId,
            offererId=stock.offer.venue.managingOffererId,
            priceCategoryLabel=(stock.priceCategory.priceCategoryLabel.label if stock.priceCategory else None),
            status=models.BookingStatus.CONFIRMED,
            depositId=(
                beneficiary.deposit.id if (beneficiary.has_active_deposit and beneficiary.deposit is not None) else None
            ),
        )

        booking.dateCreated = date_utils.get_naive_utc_now()
        booking.cancellationLimitDate = compute_booking_cancellation_limit_date(
            stock.beginningDatetime, booking.dateCreated
        )
        if beneficiary.deposit is not None and beneficiary.deposit_type == finance_models.DepositType.GRANT_17_18:
            recredit_types = [recredit.recreditType for recredit in beneficiary.deposit.recredits]
            if finance_models.RecreditType.RECREDIT_18 in recredit_types:
                booking.usedRecreditType = models.BookingRecreditType.RECREDIT_18
            elif finance_models.RecreditType.RECREDIT_17 in recredit_types:
                booking.usedRecreditType = models.BookingRecreditType.RECREDIT_17

        if is_activation_code_applicable:
            activation_code = offers_repository.get_available_activation_code(stock)
            assert activation_code  # helps mypy
            booking.activationCode = activation_code
            booking.mark_as_used(models.BookingValidationAuthorType.AUTO)
        if stock.is_automatically_used:
            booking.mark_as_used(models.BookingValidationAuthorType.AUTO)

        is_cinema_external_ticket_applicable = providers_repository.is_cinema_external_ticket_applicable(stock.offer)

        if is_cinema_external_ticket_applicable:
            offers_validation.check_offer_is_from_current_cinema_provider(stock.offer)
            tickets = external_bookings_api.book_cinema_ticket(
                venue_id=stock.offer.venueId,
                stock_id_at_providers=stock.idAtProviders,
                booking=booking,
                beneficiary=beneficiary,
            )
            booking.externalBookings = [
                models.ExternalBooking(
                    barcode=ticket.barcode,
                    seat=ticket.seat_number,
                    additional_information=ticket.additional_information,
                )
                for ticket in tickets
            ]

        if stock.offer.isEventLinkedToTicketingService:
            tickets, remaining_quantity = external_bookings_api.book_event_ticket(booking, stock, beneficiary)
            booking.externalBookings = [
                models.ExternalBooking(barcode=ticket.barcode, seat=ticket.seat_number) for ticket in tickets
            ]
            if remaining_quantity is None:
                stock.quantity = None
            else:
                stock.quantity = stock.dnBookedQuantity + remaining_quantity + booking.quantity

        stock.dnBookedQuantity += booking.quantity

        logger.info(
            "Updating dnBookedQuantity after a successful booking",
            extra={
                "booking_id": booking.id,
                "booking_quantity": booking.quantity,
                "stock_dnBookedQuantity": stock.dnBookedQuantity,
            },
        )

        db.session.add_all((booking, stock))
        db.session.flush()  # to setup relations on `booking` for `add_event()` below.

        if booking.status == models.BookingStatus.USED:
            finance_api.add_event(
                finance_models.FinanceEventMotive.BOOKING_USED,
                booking=booking,
            )
            achievements_api.unlock_achievement(booking)
    return booking


def book_offer(
    beneficiary: users_models.User,
    stock_id: int,
    quantity: int,
) -> models.Booking:
    """
    Return a booking or raise an exception if it's not possible.
    Update a user's credit information on Batch.
    """
    stock = (
        db.session.query(offers_models.Stock)
        .filter_by(id=stock_id)
        .options(
            sa_orm.joinedload(offers_models.Stock.offer)
            .joinedload(offers_models.Offer.venue)
            .joinedload(offerers_models.Venue.offererAddress)
            .joinedload(offerers_models.OffererAddress.address),
            sa_orm.joinedload(offers_models.Stock.offer)
            .joinedload(offers_models.Offer.offererAddress)
            .joinedload(offerers_models.OffererAddress.address),
        )
        .one_or_none()
    )
    if not stock:
        raise offers_exceptions.StockDoesNotExist()

    first_venue_booking = not db.session.query(
        db.session.query(models.Booking).filter(models.Booking.venueId == stock.offer.venueId).exists()
    ).scalar()

    try:
        booking = _book_offer(beneficiary, stock_id, quantity)
    except external_bookings_exceptions.ExternalBookingNotEnoughSeatsError as error:
        offers_api.edit_stock(
            stock,
            quantity=(stock.dnBookedQuantity + error.remainingQuantity),
            editing_provider=stock.offer.lastProvider,
        )
        db.session.commit()
        logger.info(
            "Could not book offer: Event has not enough seats left",
            extra={"offer_id": stock.offer.id, "provider_id": stock.offer.lastProviderId},
        )
        raise
    except external_bookings_exceptions.ExternalBookingShowDoesNotExistError:
        # Event show does not exist anymore on provider side so we delete the stock on our side
        # (can occur with cinema integrations)
        offers_api.delete_stock(stock)
        db.session.commit()
        raise

    if beneficiary.externalIds and "apps_flyer" in beneficiary.externalIds:
        apps_flyer_job.log_user_booked_offer_event_job.delay(booking.id)

    logger.info(
        "Beneficiary booked an offer",
        extra={
            "actor": beneficiary.id,
            "offer": stock.offerId,
            "stock": stock.id,
            "booking": booking.id,
            "used": booking.is_used_or_reimbursed,
            "booking_token": booking.token,
            "barcodes": [external_booking.barcode for external_booking in booking.externalBookings],
            "booking_quantity": booking.quantity,
            "stock_dnBookedQuantity": stock.dnBookedQuantity,
            "stock_quantity": stock.quantity,
        },
    )
    track_offer_booked_event(beneficiary.id, stock.offer)
    external_bookings_api.send_booking_notification_to_external_service(booking, BookingAction.BOOK)

    transactional_mails.send_user_new_booking_to_pro_email(booking, first_venue_booking)
    transactional_mails.send_individual_booking_confirmation_email_to_beneficiary(booking)

    search.async_index_offer_ids(
        [stock.offerId],
        reason=IndexationReason.BOOKING_CREATION,
    )

    update_external_user(booking.user)
    update_external_pro(stock.offer.venue.bookingEmail)

    return booking


def cancel_booking_for_finance_incident(booking: models.Booking) -> None:
    try:
        _execute_cancel_booking(
            booking=booking,
            reason=models.BookingCancellationReasons.FINANCE_INCIDENT,
            raise_if_error=True,
            cancel_related_finance_event=False,
            cancel_even_if_reimbursed=True,
        )
    except external_bookings_exceptions.ExternalBookingAlreadyCancelledError as error:
        booking.cancel_booking(
            reason=models.BookingCancellationReasons.FINANCE_INCIDENT,
            cancel_even_if_reimbursed=True,
        )
        if error.remainingQuantity is None:
            booking.stock.quantity = None
        else:
            booking.stock.quantity = booking.stock.dnBookedQuantity + error.remainingQuantity

    logger.info(
        "Booking has been cancelled",
        extra={
            "booking_id": booking.id,
            "reason": str(models.BookingCancellationReasons.FINANCE_INCIDENT),
            "booking_token": booking.token,
            "barcodes": [external_booking.barcode for external_booking in booking.externalBookings],
        },
        technical_message_id="booking.cancelled",
    )
    external_bookings_api.send_booking_notification_to_external_service(booking, BookingAction.CANCEL)
    on_commit(
        partial(
            search.async_index_offer_ids,
            [booking.stock.offerId],
            reason=IndexationReason.BOOKING_CANCELLATION,
        )
    )


def _cancel_booking(
    booking: models.Booking,
    reason: models.BookingCancellationReasons,
    *,
    cancel_even_if_used: bool = False,
    raise_if_error: bool = False,
    one_side_cancellation: bool = False,
    author_id: int | None = None,
) -> bool:
    """Cancel booking and update a user's credit information on Batch"""
    try:
        if not _execute_cancel_booking(
            booking=booking,
            reason=reason,
            cancel_even_if_used=cancel_even_if_used,
            raise_if_error=raise_if_error,
            one_side_cancellation=one_side_cancellation,
            author_id=author_id,
        ):
            return False
    except external_bookings_exceptions.ExternalBookingAlreadyCancelledError as error:
        booking.cancel_booking(
            reason=reason,
            cancel_even_if_used=cancel_even_if_used,
            author_id=author_id,
        )
        if error.remainingQuantity is None:
            booking.stock.quantity = None
        else:
            booking.stock.quantity = booking.stock.dnBookedQuantity + error.remainingQuantity
    except external_bookings_exceptions.ExternalBookingException as error:
        if raise_if_error:
            raise error

    # After UPDATE query, objet is refreshed when accessed.
    # Force refresh with joinedload to avoid N+1 queries below.
    booking = (
        db.session.query(models.Booking)
        .filter_by(id=booking.id)
        .options(
            sa_orm.joinedload(models.Booking.externalBookings),
            sa_orm.joinedload(models.Booking.stock, innerjoin=True).joinedload(
                offers_models.Stock.offer, innerjoin=True
            ),
            sa_orm.joinedload(models.Booking.user, innerjoin=True)
            .selectinload(users_models.User.deposits)
            .selectinload(finance_models.Deposit.recredits),
        )
        .one()
    )

    logger.info(
        "Booking has been cancelled",
        extra={
            "booking_id": booking.id,
            "reason": str(reason),
            "booking_token": booking.token,
            "barcodes": [external_booking.barcode for external_booking in booking.externalBookings],
        },
        technical_message_id="booking.cancelled",
    )
    batch.track_booking_cancellation(booking)
    external_bookings_api.send_booking_notification_to_external_service(booking, BookingAction.CANCEL)

    update_external_user(booking.user)
    update_external_pro(booking.venue.bookingEmail)
    on_commit(
        partial(
            search.async_index_offer_ids,
            [booking.stock.offerId],
            reason=IndexationReason.BOOKING_CANCELLATION,
        )
    )
    return True


def _execute_cancel_booking(
    booking: models.Booking,
    reason: models.BookingCancellationReasons,
    *,
    cancel_even_if_used: bool = False,
    cancel_even_if_reimbursed: bool = False,
    cancel_related_finance_event: bool = True,
    raise_if_error: bool = False,
    one_side_cancellation: bool = False,
    author_id: int | None = None,
) -> bool:
    with transaction():
        with db.session.no_autoflush:
            stock = offers_repository.get_and_lock_stock(stock_id=booking.stockId)
            db.session.refresh(booking)
            logger.info(
                "Cancelling booking...",
                extra={
                    "booking_id": booking.id,
                    "stock_dnBookedQuantity": stock.dnBookedQuantity,
                    "booking_quantity": booking.quantity,
                },
            )
            try:
                booking.cancel_booking(
                    reason=reason,
                    cancel_even_if_used=cancel_even_if_used,
                    cancel_even_if_reimbursed=cancel_even_if_reimbursed,
                    author_id=author_id,
                )
                if cancel_related_finance_event and finance_api.cancel_latest_event(booking):
                    finance_api.add_event(
                        finance_models.FinanceEventMotive.BOOKING_CANCELLED_AFTER_USE,
                        booking=booking,
                    )
                if not one_side_cancellation and booking.isExternal:
                    _cancel_external_booking(booking, stock)
            except (
                exceptions.BookingIsAlreadyUsed,
                exceptions.BookingIsAlreadyCancelled,
                finance_exceptions.NonCancellablePricingError,
            ) as e:
                if raise_if_error:
                    raise
                if is_managed_transaction():
                    mark_transaction_as_invalid()
                else:
                    db.session.rollback()
                logger.info(
                    "%s: %s",
                    type(e).__name__,
                    str(e),
                    extra={
                        "booking": booking.id,
                        "reason": str(reason),
                    },
                )
                return False
            stock.dnBookedQuantity -= booking.quantity
            if booking.activationCode and stock.quantity:
                stock.quantity -= 1
            db.session.add(booking)
            pcapi_repository.save(stock)
    return True


def _cancel_external_booking(booking: models.Booking, stock: offers_models.Stock) -> None:
    offer = stock.offer
    barcodes = [external_booking.barcode for external_booking in booking.externalBookings]

    # FIXME: `offer.lastProvider.hasTicketingService` is legacy to support old public API
    if offer.lastProvider and (
        offer.isEventLinkedToTicketingService or offer.lastProvider.hasTicketingService
    ):  # Linked to ticketing service
        venue_provider = providers_repository.get_venue_provider_by_venue_and_provider_ids(
            offer.venueId, offer.lastProvider.id
        )
        external_bookings_api.cancel_event_ticket(offer.lastProvider, stock, barcodes, True, venue_provider)
    else:  # cinema provider
        external_bookings_api.cancel_booking(stock.offer.venueId, barcodes)


def _cancel_bookings_from_stock(
    stock: offers_models.Stock,
    reason: models.BookingCancellationReasons,
    one_side_cancellation: bool = False,
    author_id: int | None = None,
) -> list[models.Booking]:
    """
    Cancel multiple bookings and update the users' credit information on Batch.
    Note that this will not reindex the stock.offer in Algolia
    """
    cancelled_bookings: list[models.Booking] = []
    for booking in stock.bookings:
        # Do not make several SQL queries per booking then rollback to savepoint for those which cannot be cancelled.
        # This optimization could avoid timeout in the backoffice when an EAN is rejected with many past bookings.
        if booking.status in (models.BookingStatus.REIMBURSED, models.BookingStatus.CANCELLED):
            continue

        cancel_even_if_used = stock.offer.isEvent
        if booking.status == models.BookingStatus.USED and not cancel_even_if_used:
            continue

        if _cancel_booking(
            booking,
            reason,
            cancel_even_if_used=cancel_even_if_used,
            one_side_cancellation=one_side_cancellation,
            author_id=author_id,
        ):
            cancelled_bookings.append(booking)

    return cancelled_bookings


def cancel_booking_by_beneficiary(user: users_models.User, booking: models.Booking) -> None:
    if not user.is_beneficiary:
        raise RuntimeError("Unexpected call to cancel_booking_by_beneficiary with non-beneficiary user %s" % user)
    validation.check_beneficiary_can_cancel_booking(user, booking)
    _cancel_booking(booking, models.BookingCancellationReasons.BENEFICIARY, raise_if_error=True)
    transactional_mails.send_booking_cancellation_emails_to_user_and_offerer(booking, booking.cancellationReason)


def cancel_booking_by_offerer(booking: models.Booking) -> None:
    validation.check_booking_can_be_cancelled(booking)
    _cancel_booking(booking, models.BookingCancellationReasons.OFFERER, raise_if_error=True)
    push_notification_job.send_cancel_booking_notification.delay([booking.id])
    transactional_mails.send_booking_cancellation_emails_to_user_and_offerer(booking, booking.cancellationReason)


def cancel_bookings_from_stock_by_offerer(
    stock: offers_models.Stock, author_id: int | None = None, user_connect_as: bool | None = None
) -> list[models.Booking]:
    if user_connect_as:
        cancellation_reason = models.BookingCancellationReasons.OFFERER_CONNECT_AS
    else:
        cancellation_reason = models.BookingCancellationReasons.OFFERER
    return _cancel_bookings_from_stock(stock, cancellation_reason, one_side_cancellation=True, author_id=author_id)


def cancel_bookings_from_rejected_offer(offer: offers_models.Offer) -> list[models.Booking]:
    cancelled_bookings = []
    for stock in offer.stocks:
        cancelled_bookings.extend(
            _cancel_bookings_from_stock(stock, models.BookingCancellationReasons.FRAUD_INAPPROPRIATE)
        )
    logger.info(
        "Cancelled bookings for rejected offer",
        extra={
            "bookings": [b.id for b in cancelled_bookings],
            "offer": offer.id,
        },
    )

    return cancelled_bookings


def cancel_booking_for_fraud(booking: models.Booking, reason: users_constants.SuspensionReason) -> None:
    validation.check_booking_can_be_cancelled(booking)
    cancelled = _cancel_booking(
        booking,
        (
            models.BookingCancellationReasons.FRAUD_SUSPICION
            if reason == users_constants.SuspensionReason.FRAUD_SUSPICION
            else models.BookingCancellationReasons.FRAUD
        ),
    )
    if not cancelled:
        return
    logger.info("Cancelled booking for fraud reason", extra={"booking": booking.id, "reason": reason.value})
    transactional_mails.send_booking_cancellation_emails_to_user_and_offerer(booking, booking.cancellationReason)


def cancel_booking_on_user_requested_account_suspension(booking: models.Booking) -> None:
    validation.check_booking_can_be_cancelled(booking)
    cancelled = _cancel_booking(booking, models.BookingCancellationReasons.BENEFICIARY)
    if not cancelled:
        return
    logger.info(
        "Cancelled booking on user-requested account suspension",
        extra={"booking": booking.id},
    )
    transactional_mails.send_booking_cancellation_emails_to_user_and_offerer(booking, booking.cancellationReason)


def cancel_booking_on_closed_offerer(booking: models.Booking, author_id: int | None = None) -> None:
    validation.check_booking_can_be_cancelled(booking)
    try:
        cancelled = _cancel_booking(booking, models.BookingCancellationReasons.OFFERER_CLOSED, author_id=author_id)
    except external_bookings_exceptions.ExternalBookingException as exc:
        logger.info(
            "API error while cancelling external booking, try to cancel unilaterally",
            extra={"exc": exc, "booking": booking.id},
        )
        cancelled = _cancel_booking(
            booking, models.BookingCancellationReasons.OFFERER_CLOSED, one_side_cancellation=True, author_id=author_id
        )
    if not cancelled:
        return
    logger.info("Cancelled booking on closed offerer", extra={"booking": booking.id})
    transactional_mails.send_booking_cancellation_emails_to_user_and_offerer(booking, booking.cancellationReason)


def mark_as_used(booking: models.Booking, validation_author_type: models.BookingValidationAuthorType) -> None:
    validation.check_is_usable(booking)

    booking.mark_as_used(validation_author_type)

    finance_api.add_event(finance_models.FinanceEventMotive.BOOKING_USED, booking=booking)
    achievements_api.unlock_achievement(booking)

    db.session.flush()

    logger.info(
        "Booking was marked as used",
        extra={"booking_id": booking.id},
        technical_message_id="booking.used",
    )

    update_external_user(booking.user)


def mark_as_used_with_uncancelling(
    booking: models.Booking, validation_author_type: models.BookingValidationAuthorType
) -> None:
    """Mark a booking as used from cancelled status.

    This function should be called only if the booking
    has been cancelled by mistake or fraudulently after the offer was
    retrieved (for example, when a beneficiary retrieved a book from a
    library and then cancelled their booking before the library marked
    it as used).
    """
    # I'm not 100% sure the transaction is required here
    # It is not clear to me whether or not Flask-SQLAlchemy will make
    # a rollback if we raise a validation exception.
    # Since I lock the stock, I really want to make sure the lock is
    # removed ASAP.
    if (
        booking.deposit
        and booking.deposit.expirationDate
        and booking.deposit.expirationDate < date_utils.get_naive_utc_now()
    ):
        raise exceptions.BookingDepositCreditExpired()

    if booking.status == models.BookingStatus.CANCELLED:
        booking.uncancel_booking_set_used()
        stock = offers_repository.get_and_lock_stock(stock_id=booking.stockId)
        stock.dnBookedQuantity += booking.quantity
        db.session.add(stock)
        db.session.flush()
    booking.validationAuthorType = validation_author_type
    db.session.add(booking)

    finance_api.add_event(
        finance_models.FinanceEventMotive.BOOKING_USED_AFTER_CANCELLATION,
        booking=booking,
    )
    achievements_api.unlock_achievement(booking)

    db.session.flush()
    logger.info("Booking was uncancelled and marked as used", extra={"bookingId": booking.id})

    update_external_user(booking.user)


def mark_as_cancelled(
    booking: models.Booking,
    reason: models.BookingCancellationReasons,
    one_side_cancellation: bool = False,
    author_id: int | None = None,
) -> None:
    """
    A booking can be cancelled only if it has not been cancelled before and if
    it has not been refunded. Since a payment can be retried, it is safer to
    say that a booking with payment, whatever its status, should be considered
    refunded. A used booking without payment can be marked as cancelled by an
    admin user.

    One side cancellation. Mainly to be used from the backoffice. The external provider API
    is not called and the booking is cancelled on our side.
    """
    if booking.status == models.BookingStatus.CANCELLED:
        raise exceptions.BookingIsAlreadyCancelled()

    if finance_repository.has_reimbursement(booking):
        raise exceptions.BookingIsAlreadyRefunded()

    if one_side_cancellation:
        if (
            not models.BookingCancellationReasons.is_from_backoffice(reason)
            or (
                booking.stock.offer.lastProvider
                and booking.stock.offer.lastProvider.localClass
                not in constants.ONE_SIDE_BOOKINGS_CANCELLATION_PROVIDERS
            )
            or (
                booking.stock.beginningDatetime
                and booking.stock.beginningDatetime < date_utils.get_naive_utc_now() - datetime.timedelta(days=15)
            )
        ):
            raise exceptions.OneSideCancellationForbidden()

    _cancel_booking(
        booking=booking,
        reason=reason,
        cancel_even_if_used=True,
        raise_if_error=True,
        one_side_cancellation=one_side_cancellation,
        author_id=author_id,
    )

    if one_side_cancellation:
        logging.info("External booking cancelled unilaterally", extra={"booking_id": booking.id})
        assert booking.stock.beginningDatetime
        if booking.stock.beginningDatetime < date_utils.get_naive_utc_now():
            transactional_mails.send_booking_cancelled_unilaterally_provider_support_email(booking)
        else:
            transactional_mails.send_booking_cancellation_by_beneficiary_to_pro_email(booking, one_side_cancellation)
    else:
        transactional_mails.send_booking_cancellation_by_beneficiary_to_pro_email(booking)


def mark_as_unused(booking: models.Booking) -> None:
    validation.check_can_be_mark_as_unused(booking)
    finance_api.cancel_latest_event(booking)
    finance_api.add_event(
        finance_models.FinanceEventMotive.BOOKING_UNUSED,
        booking=booking,
    )
    booking.mark_as_unused_set_confirmed()

    db.session.flush()

    logger.info(
        "Booking was marked as unused",
        extra={"booking_id": booking.id},
        technical_message_id="booking.unused",
    )

    update_external_user(booking.user)
    update_external_pro(booking.venue.bookingEmail)


def compute_booking_cancellation_limit_date(
    event_beginning: datetime.datetime | None, booking_date: datetime.datetime
) -> datetime.datetime | None:
    if event_beginning is None:
        return None

    event_beginning = serialization_utils.as_utc_without_timezone(event_beginning)
    before_event_cancellation_date = event_beginning - constants.CONFIRM_BOOKING_BEFORE_EVENT_DELAY
    after_booking_cancellation_date = booking_date + constants.CONFIRM_BOOKING_AFTER_CREATION_DELAY

    earliest_cancellation_date = min(before_event_cancellation_date, after_booking_cancellation_date)

    return max(earliest_cancellation_date, booking_date)


def update_cancellation_limit_dates(
    bookings_to_update: list[models.Booking], new_beginning_datetime: datetime.datetime
) -> list[models.Booking]:
    for booking in bookings_to_update:
        booking.cancellationLimitDate = _compute_edition_cancellation_limit_date(
            event_beginning=new_beginning_datetime,
            edition_date=date_utils.get_naive_utc_now(),
        )
    db.session.add_all(bookings_to_update)
    db.session.flush()
    return bookings_to_update


def _compute_edition_cancellation_limit_date(
    event_beginning: datetime.datetime, edition_date: datetime.datetime
) -> datetime.datetime:
    after_edition_cancellation_date = edition_date + constants.CONFIRM_BOOKING_AFTER_CREATION_DELAY
    return min(event_beginning, after_edition_cancellation_date)


def recompute_dnBookedQuantity(stock_ids: list[int]) -> None:
    """
    Changes are not committed within this function, use db.session.commit() if necessary.
    """
    query = f"""
      WITH bookings_per_stock AS (
        SELECT
          stock.id AS stock_id,
          COALESCE(SUM(booking.quantity), 0) AS total_bookings
        FROM stock
        -- The `NOT status CANCELLED` condition MUST be part of the JOIN.
        -- If it were part of the WHERE clause, that would exclude
        -- stocks that only have cancelled bookings.
        LEFT OUTER JOIN booking
          ON booking."stockId" = stock.id
          AND booking.status != '{models.BookingStatus.CANCELLED.value}'
        WHERE stock.id IN :stock_ids
        GROUP BY stock.id
      )
      UPDATE stock
      SET "dnBookedQuantity" = bookings_per_stock.total_bookings
      FROM bookings_per_stock
      WHERE stock.id = bookings_per_stock.stock_id
    """
    db.session.execute(sa.text(query), {"stock_ids": tuple(stock_ids)})


def auto_mark_as_used_after_event() -> None:
    """Automatically mark as used bookings that correspond to events that
    have happened (with a delay).
    """
    if not FeatureToggle.UPDATE_BOOKING_USED.is_active():
        raise ValueError("This function is behind a deactivated feature flag.")

    now = date_utils.get_naive_utc_now()
    threshold = now - constants.AUTO_USE_AFTER_EVENT_TIME_DELAY

    # Revisit with SQLAlchemy 2.
    #
    # I tried to update and select bookings in a single query, like this:
    #     WITH updated AS (
    #       UPDATE booking
    #       SET "dateUsed" = :now, status = 'USED'
    #       FROM stock WHERE ...
    #       RETURNING booking.id
    #     )
    #     SELECT ... FROM booking JOIN ...
    #     WHERE booking.id IN (select id from updated)
    #
    # In SQLAlchemy:
    #     individual_updated = (
    #         sa.update(models.Booking)
    #         .returning(models.Booking.id)
    #         .where(
    #             models.Booking.status == models.BookingStatus.CONFIRMED,
    #             models.Booking.stockId == offers_models.Stock.id,
    #             offers_models.Stock.beginningDatetime < threshold,
    #         )
    #         .values(dateUsed=now, status=models.BookingStatus.USED)
    #     )
    #     individual_select = sa.select(models.Booking).options(
    #         sa_orm.joinedload(models.Booking.stock, innerjoin=True),
    #         sa_orm.joinedload(models.Booking.venue, innerjoin=True),
    #     )
    #     individual_bookings = db.session.execute(
    #         individual_select.where(models.Booking.id.in_(sa.select([individual_updated.cte(name="updated").c.id]))),
    #         execution_options={"synchronize_session": True},
    #     )
    #
    # But it does not work: the SELECT part does not see updated
    # columns (and here we need to see the newly set value of
    # `dateUsed`, otherwise `finance.api.add_event()` raises an
    # error).
    #
    # I think that it might be possible to make it work by using
    # `returning(models.Booking)` instead of `returning(models.Booking.id)`, and
    # joining related tables. SQLAlchemy would know that what it gets
    # from the CTE must be used to populate `models.Booking` objects.
    # However, this is only possible in SQLAlchemy 2.

    # Individual bookings: update and add a finance event for each one.
    db.session.execute(
        sa.update(models.Booking)
        .where(
            models.Booking.status == models.BookingStatus.CONFIRMED,
            models.Booking.stockId == offers_models.Stock.id,
            offers_models.Stock.beginningDatetime < threshold,
        )
        .values(
            dateUsed=now, status=models.BookingStatus.USED, validationAuthorType=models.BookingValidationAuthorType.AUTO
        ),
        execution_options={"synchronize_session": False},
    )
    # `dateUsed` is precise enough that it's very unlikely to get a
    # booking that was marked as used from another channel (and that
    # would already have an event). If it happened, `add_event` would
    # fail because of the PostgreSQL partially unique constraint on
    # `bookingId`.
    individual_bookings = (
        db.session.query(models.Booking)
        .filter_by(dateUsed=now)
        .options(
            sa_orm.joinedload(models.Booking.stock, innerjoin=True).joinedload(offers_models.Stock.offer),
            sa_orm.joinedload(models.Booking.venue, innerjoin=True),
            sa_orm.joinedload(models.Booking.user).selectinload(users_models.User.achievements),
        )
    )
    n_individual_bookings_updated = 0
    for booking in individual_bookings:
        finance_api.add_event(
            finance_models.FinanceEventMotive.BOOKING_USED,
            booking=booking,
        )
        achievements_api.unlock_achievement(booking)
        n_individual_bookings_updated += 1

    # Collective bookings: update and add a finance event for each
    # one. We do the same as above, except that we add a log for data
    # analysis.
    db.session.execute(
        sa.update(educational_models.CollectiveBooking)
        .where(
            educational_models.CollectiveBooking.status == educational_models.CollectiveBookingStatus.CONFIRMED,
            educational_models.CollectiveBooking.collectiveStockId == educational_models.CollectiveStock.id,
            educational_models.CollectiveStock.endDatetime < threshold,
        )
        .values(dateUsed=now, status=educational_models.CollectiveBookingStatus.USED),
        execution_options={"synchronize_session": False},
    )
    collective_bookings = (
        db.session.query(educational_models.CollectiveBooking)
        .filter_by(dateUsed=now)
        .options(
            sa_orm.joinedload(educational_models.CollectiveBooking.collectiveStock, innerjoin=True),
            sa_orm.joinedload(educational_models.CollectiveBooking.venue, innerjoin=True),
        )
    )
    n_collective_bookings_updated = 0
    for collective_booking in collective_bookings:
        finance_api.add_event(
            finance_models.FinanceEventMotive.BOOKING_USED,
            booking=collective_booking,
        )
        n_collective_bookings_updated += 1
        educational_utils.log_information_for_data_purpose(
            event_name="BookingUsed",
            extra_data={"bookingId": collective_booking.id, "stockId": collective_booking.collectiveStockId},
            uai=None,
            user_role=None,
        )

    db.session.commit()

    logger.info(
        "Automatically marked bookings as used after event",
        extra={
            "dateUsed": now,
            "individualBookingsUpdatedCount": n_individual_bookings_updated,
            "collectiveBookingsUpdatedCount": n_collective_bookings_updated,
        },
    )


def get_individual_bookings_from_stock(
    stock_id: int,
) -> typing.Generator[sa.Row[tuple[int, int]], None, None]:
    query = (
        db.session.query(
            models.Booking.id,
            models.Booking.userId,
        )
        .filter(
            models.Booking.stockId == stock_id,
            models.Booking.status != models.BookingStatus.CANCELLED,
        )
        .distinct()
    )
    yield from query.yield_per(1_000)


def archive_old_bookings() -> None:
    date_condition = models.Booking.dateCreated < date_utils.get_naive_utc_now() - constants.ARCHIVE_DELAY

    query_old_booking_ids = (
        db.session.query(models.Booking)
        .join(models.Booking.stock)
        .join(offers_models.Stock.offer)
        .join(models.Booking.activationCode)
        .filter(date_condition)
        .filter(
            offers_models.Offer.hasUrl,
            offers_models.ActivationCode.id.is_not(None),
        )
        .with_entities(models.Booking.id)
        .union(
            db.session.query(models.Booking)
            .join(models.Booking.stock)
            .join(offers_models.Stock.offer)
            .filter(date_condition)
            .filter(models.Booking.display_even_if_used)
            .with_entities(models.Booking.id)
        )
    )

    number_updated = (
        db.session.query(models.Booking)
        .filter(models.Booking.id.in_(query_old_booking_ids))
        .update(
            {"displayAsEnded": True},
            synchronize_session=False,
        )
    )
    db.session.commit()

    logger.info(
        "Old activation code bookings archived (displayAsEnded=True)",
        extra={
            "archivedBookings": number_updated,
        },
    )


def handle_expired_individual_bookings() -> None:
    logger.info("[handle_expired_individual_bookings] Start")

    try:
        _cancel_expired_individual_bookings()
    except Exception as e:
        logger.exception("Error in cancel_expired_individual_bookings : %s", e)

    try:
        _notify_users_of_expired_individual_bookings()
    except Exception as e:
        logger.exception("Error in notify_users_of_expired_individual_bookings : %s", e)

    try:
        _notify_offerers_of_expired_individual_bookings()
    except Exception as e:
        logger.exception("Error in notify_offerers_of_expired_individual_bookings : %s", e)

    logger.info("[handle_expired_individual_bookings] End")


def _cancel_expired_individual_bookings(batch_size: int = 500) -> None:
    expiring_individual_bookings_query = repository.find_expiring_individual_bookings_query()
    expiring_booking_ids = [b[0] for b in expiring_individual_bookings_query.with_entities(models.Booking.id).all()]

    logger.info("[cancel_expired_bookings] %d expiring bookings to cancel", len(expiring_booking_ids))

    # we commit here to make sure there is no unexpected objects in SQLA cache before the update,
    # as we use synchronize_session=False
    db.session.commit()

    start_index = 0
    updated_total = 0

    while start_index < len(expiring_booking_ids):
        booking_ids_to_update = expiring_booking_ids[start_index : start_index + batch_size]
        updated = (
            db.session.query(models.Booking)
            .filter(models.Booking.id.in_(booking_ids_to_update))
            .update(
                {
                    "status": models.BookingStatus.CANCELLED,
                    "cancellationReason": models.BookingCancellationReasons.EXPIRED,
                    "cancellationDate": date_utils.get_naive_utc_now(),
                },
                synchronize_session=False,
            )
        )
        # Recompute denormalized stock quantity
        stocks_to_recompute = [
            row[0]
            for row in db.session.query(models.Booking.stockId)
            .filter(models.Booking.id.in_(booking_ids_to_update))
            .distinct()
            .all()
        ]
        recompute_dnBookedQuantity(stocks_to_recompute)
        db.session.commit()

        updated_total += updated

        logger.info(
            "[cancel_expired_bookings] %d Bookings have been cancelled in this batch",
            updated,
        )

        start_index += batch_size

    logger.info("[cancel_expired_bookings] %d Bookings have been cancelled", updated_total)


def _notify_users_of_expired_individual_bookings(expired_on: datetime.date | None = None) -> None:
    expired_on = expired_on or datetime.date.today()

    logger.info("[notify_users_of_expired_bookings] Start")
    user_ids = repository.find_user_ids_with_expired_individual_bookings(expired_on)
    notified_users_str = []
    for user_id in user_ids:
        user = db.session.get(users_models.User, user_id)
        assert user  # helps mypy
        transactional_mails.send_expired_bookings_to_beneficiary_email(
            user,
            repository.get_expired_individual_bookings_for_user(user),
        )
        notified_users_str.append(user.id)

    logger.info(
        "[notify_users_of_expired_bookings] %d Users have been notified: %s",
        len(notified_users_str),
        notified_users_str,
    )


def _notify_offerers_of_expired_individual_bookings(expired_on: datetime.date | None = None) -> None:
    expired_on = expired_on or datetime.date.today()
    logger.info("[notify_offerers_of_expired_bookings] Start")

    expired_individual_bookings_grouped_by_offerer = {
        offerer: list(bookings)
        for offerer, bookings in groupby(
            repository.find_expired_individual_bookings_ordered_by_offerer(expired_on),
            attrgetter("offerer"),
        )
    }

    notified_offerers = []

    for offerer, bookings in expired_individual_bookings_grouped_by_offerer.items():
        transactional_mails.send_bookings_expiration_to_pro_email(bookings)
        notified_offerers.append(offerer)

    logger.info(
        "[notify_users_of_expired_individual_bookings] %d Offerers have been notified: %s",
        len(notified_offerers),
        notified_offerers,
    )


def cancel_unstored_external_bookings() -> None:
    """
    Cancel external bookings if we don't have a corresponding Booking object on our side.
        When a user wants to book an offer that can be booked by an external partner, we first request a booking
        from the partner, and then we try to create a Booking in our database.
        If the second action fails, we need to request the partner to cancel the booking on their side. To do that,
        we push the information to a Redis queue, and regularly check whether we have a corresponding Booking.
    To avoid cancel external bookings in process of pass culture booking, we check if the barcode has an age of 1 min
    in the queue, if it doesn't it will be enqueued again and wait for the next time.
    """
    while True:
        external_booking_info = queue.pop_from_queue(constants.REDIS_EXTERNAL_BOOKINGS_NAME)
        if not external_booking_info:
            break
        if (
            date_utils.get_naive_utc_now().timestamp() - external_booking_info["timestamp"]
            < constants.EXTERNAL_BOOKINGS_MINIMUM_ITEM_AGE_IN_QUEUE
        ):
            queue.add_to_queue(
                constants.REDIS_EXTERNAL_BOOKINGS_NAME,
                external_booking_info,
                at_head=True,
            )
            break

        barcode = external_booking_info["barcode"]
        external_bookings = db.session.query(models.ExternalBooking).filter_by(barcode=barcode).all()
        if not external_bookings:
            booking_type = external_booking_info.get("booking_type")
            if booking_type == constants.RedisExternalBookingType.EVENT:
                provider_id = external_booking_info["cancel_event_info"]["provider_id"]
                provider = providers_repository.get_active_provider_by_id(provider_id)
                stock_id = external_booking_info["cancel_event_info"]["stock_id"]
                stock = db.session.query(offers_models.Stock).filter_by(id=stock_id).one_or_none()
                if not stock or not provider:
                    logger.error("Couldn't find stock or provider for external booking", extra=external_booking_info)
                    raise external_bookings_exceptions.ExternalBookingException(
                        "Error while canceling unstored ticket. Barcode: ",
                        str(barcode),
                    )
                venue_provider = providers_repository.get_venue_provider_by_venue_and_provider_ids(
                    stock.offer.venueId, provider.id
                )
                external_bookings_api.cancel_event_ticket(provider, stock, [barcode], False, venue_provider)
            else:
                venue_id = int(external_booking_info["venue_id"])
                external_bookings_api.cancel_booking(venue_id, [barcode])


def cancel_ems_external_bookings() -> None:
    EMS_DEADLINE_BEFORE_CANCELLING = 90
    redis_client = current_app.redis_client
    ems_queue = EMS_EXTERNAL_BOOKINGS_TO_CANCEL

    while redis_client.llen(ems_queue) > 0:
        booking_to_cancel = json.loads(redis_client.rpop(ems_queue))
        cinema_id, token, timestamp = (
            booking_to_cancel["cinema_id"],
            booking_to_cancel["token"],
            booking_to_cancel["timestamp"],
        )

        if timestamp + EMS_DEADLINE_BEFORE_CANCELLING > date_utils.get_naive_utc_now().timestamp():
            # This is the oldest booking to cancel we have in the queue and its too recent.
            redis_client.rpush(ems_queue, json.dumps(booking_to_cancel))
            return

        client = EMSAPIClient(cinema_id=cinema_id)
        try:
            tickets = client.get_ticket(token)
        except EMSAPIException as exc:
            logger.info(
                "Fail to fetch the external booking informations with exception: %s",
                str(exc),
                extra={"token": token, "cinema_id": cinema_id},
            )
            continue

        try:
            client.cancel_booking_with_tickets(tickets)
        except (requests_exceptions.ReadTimeout, requests_exceptions.Timeout):
            logger.info(
                "Fail to cancel external booking due to timeout", extra={"token": token, "cinema_id": cinema_id}
            )
        except EMSAPIException as exc:
            logger.info(
                "Fail to cancel external booking due to EMSAPIException: %s",
                str(exc),
                extra={"token": token, "cinema_id": cinema_id},
            )


def is_external_event_booking_visible(offer: offers_models.Offer, stock: offers_models.Stock) -> bool:
    if offer.withdrawalType == offers_models.WithdrawalTypeEnum.IN_APP:
        if stock.beginningDatetime:
            delta = stock.beginningDatetime - date_utils.get_naive_utc_now()
            return delta.total_seconds() < NUMBER_SECONDS_HIDE_QR_CODE
    return True


def is_voucher_displayed(offer: offers_models.Offer, isExternal: bool) -> bool:
    if offer.subcategoryId == SEANCE_CINE.id:
        return not isExternal

    return not offer.isEvent


def has_email_been_sent(stock: offers_models.Stock, withdrawal_delay: int | None) -> bool:
    if withdrawal_delay and stock.beginningDatetime:
        delta = stock.beginningDatetime - date_utils.get_naive_utc_now()
        return delta.total_seconds() < withdrawal_delay
    return False
