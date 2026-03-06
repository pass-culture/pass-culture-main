import logging
from functools import partial

import pcapi.core.bookings.models as bookings_models
import pcapi.core.finance.models as finance_models
import pcapi.core.offers.models as offers_models
import pcapi.core.subscription.models as subscription_models
from pcapi.core.external.batch.models import BatchEvent
from pcapi.core.external.batch.utils import format_date
from pcapi.core.external.batch.utils import shorten_for_batch
from pcapi.core.mails.transactional.utils import format_price
from pcapi.tasks import batch_tasks
from pcapi.utils.transaction_manager import on_commit

from .serialization import TrackBatchEventRequest
from .serialization import TrackBatchEventsRequest


logger = logging.getLogger(__name__)


def _format_offer_attributes(offer: offers_models.Offer) -> dict:
    stock = min(
        offer.bookableStocks,
        default=None,
        key=lambda stock: (stock.bookingLimitDatetime is None, stock.bookingLimitDatetime, stock.price),
    )
    stock_quantity: int | None = None
    event_date: str | None = None
    expiry_date: str | None = None
    if stock is not None:
        if stock.remainingQuantity != "unlimited":
            stock_quantity = stock.remainingQuantity
        event_date = format_date(stock.beginningDatetime)
        expiry_date = format_date(stock.bookingLimitDatetime)

    offer_attributes = {
        "offer_id": offer.id,
        "offer_name": shorten_for_batch(offer.name, max_length=64, placeholder="...", preserve_words=True),
        "offer_category": offer.categoryId,
        "offer_subcategory": offer.subcategoryId,
        "offer_type": "duo" if offer.isDuo else "solo",
        "stock": stock_quantity,
        "event_date": event_date,
        "expiry_date": expiry_date,
    }
    return {key: value for key, value in offer_attributes.items() if value is not None}


def track_deposit_activated_event(user_id: int, deposit: finance_models.Deposit) -> None:
    event_name = BatchEvent.USER_DEPOSIT_ACTIVATED
    event_payload = {"deposit_type": deposit.type.value, "deposit_amount": round(deposit.amount)}
    payload = TrackBatchEventRequest(event_name=event_name, event_payload=event_payload, user_id=user_id)
    on_commit(partial(batch_tasks.track_event_task.delay, payload))


def track_account_recredited(user_id: int, deposit: finance_models.Deposit, deposit_count: int) -> None:
    event_name = BatchEvent.RECREDITED_ACCOUNT
    user = deposit.user
    event_payload = {
        "deposit_amount": round(deposit.amount),
        "formatted_deposit_amount": format_price(deposit.amount, user, replace_free_amount=False),
        "deposit_type": deposit.type.value,
        "deposits_count": deposit_count,
        "deposit_expiration_date": format_date(deposit.expirationDate),
    }
    payload = TrackBatchEventRequest(event_name=event_name, event_payload=event_payload, user_id=user_id)
    on_commit(partial(batch_tasks.track_event_task.delay, payload))


def track_identity_check_started_event(user_id: int, fraud_check_type: subscription_models.FraudCheckType) -> None:
    event_name = BatchEvent.USER_IDENTITY_CHECK_STARTED
    payload = TrackBatchEventRequest(
        event_name=event_name, event_payload={"type": fraud_check_type.value}, user_id=user_id
    )
    on_commit(partial(batch_tasks.track_event_task.delay, payload))


def track_ubble_ko_event(user_id: int, reason_code: subscription_models.FraudReasonCode) -> None:
    event_name = BatchEvent.HAS_UBBLE_KO_STATUS
    payload = TrackBatchEventRequest(
        event_name=event_name, event_payload={"error_code": reason_code.value}, user_id=user_id
    )
    on_commit(partial(batch_tasks.track_event_task.delay, payload))


def track_offer_added_to_favorites_event(user_id: int, offer: offers_models.Offer) -> None:
    event_name = BatchEvent.HAS_ADDED_OFFER_TO_FAVORITES
    formatted_offer_attributes = _format_offer_attributes(offer)
    payload = TrackBatchEventRequest(event_name=event_name, event_payload=formatted_offer_attributes, user_id=user_id)
    on_commit(partial(batch_tasks.track_event_task.delay, payload))


def track_offer_booked_event(user_id: int, offer: offers_models.Offer) -> None:
    event_name = BatchEvent.HAS_BOOKED_OFFER
    formatted_offer_attributes = _format_offer_attributes(offer)
    payload = TrackBatchEventRequest(event_name=event_name, event_payload=formatted_offer_attributes, user_id=user_id)
    on_commit(partial(batch_tasks.track_event_task.delay, payload))


def track_booking_cancellation(booking: bookings_models.Booking) -> None:
    from pcapi.core.users.api import get_domains_credit

    event_name = BatchEvent.RECREDIT_ACCOUNT_CANCELLATION
    user = booking.user
    offer = booking.stock.offer
    domains_credit = get_domains_credit(user)
    assert domains_credit  # helps mypy
    event_payload = {
        "credit": domains_credit.all.remaining,
        "formatted_credit": format_price(domains_credit.all.remaining, user, replace_free_amount=False),
        "offer_id": offer.id,
        "offer_name": shorten_for_batch(offer.name, max_length=64, placeholder="...", preserve_words=True),
        "offer_price": booking.total_amount,
        "formatted_offer_price": format_price(booking.total_amount, user),
    }
    payload = TrackBatchEventRequest(event_name=event_name, event_payload=event_payload, user_id=user.id)
    on_commit(partial(batch_tasks.track_event_task.delay, payload))


def send_users_reminders_for_offer(user_ids: list[int], offer: offers_models.Offer) -> None:
    event_name = BatchEvent.FUTURE_OFFER_ACTIVATED
    formatted_offer_attributes = _format_offer_attributes(offer)

    trigger_events: list[TrackBatchEventRequest] = []
    for user_id in user_ids:
        trigger_events.append(
            TrackBatchEventRequest(event_name=event_name, event_payload=formatted_offer_attributes, user_id=user_id)
        )

    payload = TrackBatchEventsRequest(trigger_events=trigger_events)
    on_commit(partial(batch_tasks.track_event_bulk_task.delay, payload))


def track_has_received_bonus(user_id: int) -> None:
    event_name = BatchEvent.HAS_RECEIVED_BONUS
    event_payload = {
        "has_received_bonus": True,
    }
    payload = TrackBatchEventRequest(event_name=event_name, event_payload=event_payload, user_id=user_id)
    on_commit(partial(batch_tasks.track_event_task.delay, payload))
