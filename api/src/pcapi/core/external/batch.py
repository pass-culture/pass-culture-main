import logging
from datetime import datetime

import pcapi.core.bookings.models as bookings_models
import pcapi.core.finance.models as finance_models
import pcapi.core.fraud.models as fraud_models
import pcapi.core.offers.models as offers_models
from pcapi.core.cultural_survey import models as cultural_survey_models
from pcapi.core.external.attributes import models as attributes_models
from pcapi.core.external.batch_utils import shorten_for_batch
from pcapi.notifications.push.trigger_events import BatchEvent
from pcapi.notifications.push.trigger_events import TrackBatchEventRequest
from pcapi.notifications.push.trigger_events import TrackBatchEventsRequest
from pcapi.tasks import batch_tasks


logger = logging.getLogger(__name__)


BATCH_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def update_user_attributes(
    user_id: int,
    user_attributes: attributes_models.UserAttributes,
    cultural_survey_answers: dict[str, list[str]] | None = None,
    batch_extra_data: dict[str, datetime] | None = None,
) -> None:
    if user_attributes.is_pro:
        return

    formatted_attributes = format_user_attributes(
        user_attributes, cultural_survey_answers=cultural_survey_answers, batch_extra_data=batch_extra_data
    )
    payload = batch_tasks.UpdateBatchAttributesRequest(attributes=formatted_attributes, user_id=user_id)

    batch_tasks.update_user_attributes_android_task.delay(payload)
    batch_tasks.update_user_attributes_ios_task.delay(payload)


def format_user_attributes(
    user_attributes: attributes_models.UserAttributes,
    cultural_survey_answers: dict[str, list[str]] | None = None,
    batch_extra_data: dict[str, datetime] | None = None,
) -> dict:
    # https://doc.batch.com/api/custom-data-api/set-update/#post-data
    attributes = {
        "date(u.date_created)": _format_date(user_attributes.date_created),
        "date(u.date_of_birth)": _format_date(user_attributes.date_of_birth),
        "date(u.deposit_activation_date)": _format_date(user_attributes.deposit_activation_date),
        "date(u.deposit_expiration_date)": _format_date(user_attributes.deposit_expiration_date),
        "date(u.last_booking_date)": _format_date(user_attributes.last_booking_date),
        "u.credit": int(user_attributes.domains_credit.all.remaining * 100) if user_attributes.domains_credit else None,
        "u.city": user_attributes.city,
        "u.departement_code": user_attributes.departement_code,
        "u.deposits_count": user_attributes.deposits_count,
        "u.first_name": user_attributes.first_name,
        "u.has_completed_id_check": user_attributes.has_completed_id_check,
        "u.is_beneficiary": user_attributes.is_beneficiary,
        "u.is_current_beneficiary": user_attributes.is_current_beneficiary,
        "u.is_former_beneficiary": user_attributes.is_former_beneficiary,
        "u.last_name": user_attributes.last_name,
        "u.marketing_email_subscription": user_attributes.marketing_email_subscription,
        "u.marketing_push_subscription": user_attributes.marketing_push_subscription,
        "ut.permanent_theme_preference": user_attributes.subscribed_themes or None,
        "u.postal_code": user_attributes.postal_code,
        "ut.roles": user_attributes.roles if user_attributes.roles else None,
        "u.booking_count": user_attributes.booking_count,
        "u.booking_venues_count": user_attributes.booking_venues_count,
        "u.booked_offer_categories_count": len(user_attributes.booking_categories),
        "u.most_booked_subcategory": user_attributes.most_booked_subcategory,
        "u.most_booked_movie_genre": user_attributes.most_booked_movie_genre,
        "u.most_booked_music_type": user_attributes.most_booked_music_type,
        "ut.most_favorite_offer_subcat": user_attributes.most_favorite_offer_subcategories,  # max 30 char.
        "u.eligibility": user_attributes.eligibility.value if user_attributes.eligibility else None,
        "u.is_eligible": user_attributes.is_eligible,
        "u.last_recredit_type": (
            user_attributes.last_recredit_type.value if user_attributes.last_recredit_type else None
        ),
    }

    for product_use_date_key, product_use_date_value in user_attributes.products_use_date.items():
        attributes[f"date(u.{product_use_date_key})"] = _format_date(product_use_date_value)

    # A Batch tag can't be an empty list, otherwise the API returns an error
    if user_attributes.booking_categories:
        attributes["ut.booking_categories"] = user_attributes.booking_categories
    if user_attributes.booking_subcategories:
        attributes["ut.booking_subcategories"] = user_attributes.booking_subcategories

    if cultural_survey_answers and (
        intended_categories := cultural_survey_answers.get(
            cultural_survey_models.CulturalSurveyQuestionEnum.PROJECTIONS.value, []
        )
    ):
        attributes["ut.intended_categories"] = intended_categories

    if batch_extra_data:
        attributes["date(u.last_status_update_date)"] = _format_date(batch_extra_data["last_status_update_date"])

    if user_attributes.achievements:
        attributes["ut.achievements"] = user_attributes.achievements

    return attributes


def _format_date(date: datetime | None) -> str | None:
    return date.strftime(BATCH_DATETIME_FORMAT) if date else None


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
        event_date = _format_date(stock.beginningDatetime)
        expiry_date = _format_date(stock.bookingLimitDatetime)

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
    batch_tasks.track_event_task.delay(payload)


def track_account_recredited(user_id: int, deposit: finance_models.Deposit, deposit_count: int) -> None:
    event_name = BatchEvent.RECREDITED_ACCOUNT
    event_payload = {
        "deposit_amount": round(deposit.amount),
        "deposit_type": deposit.type.value,
        "deposits_count": deposit_count,
        "deposit_expiration_date": _format_date(deposit.expirationDate),
    }
    payload = TrackBatchEventRequest(event_name=event_name, event_payload=event_payload, user_id=user_id)
    batch_tasks.track_event_task.delay(payload)


def track_identity_check_started_event(user_id: int, fraud_check_type: fraud_models.FraudCheckType) -> None:
    event_name = BatchEvent.USER_IDENTITY_CHECK_STARTED
    payload = TrackBatchEventRequest(
        event_name=event_name, event_payload={"type": fraud_check_type.value}, user_id=user_id
    )
    batch_tasks.track_event_task.delay(payload)


def track_ubble_ko_event(user_id: int, reason_code: fraud_models.FraudReasonCode) -> None:
    event_name = BatchEvent.HAS_UBBLE_KO_STATUS
    payload = TrackBatchEventRequest(
        event_name=event_name, event_payload={"error_code": reason_code.value}, user_id=user_id
    )
    batch_tasks.track_event_task.delay(payload)


def track_offer_added_to_favorites_event(user_id: int, offer: offers_models.Offer) -> None:
    event_name = BatchEvent.HAS_ADDED_OFFER_TO_FAVORITES
    formatted_offer_attributes = _format_offer_attributes(offer)
    payload = TrackBatchEventRequest(event_name=event_name, event_payload=formatted_offer_attributes, user_id=user_id)
    batch_tasks.track_event_task.delay(payload)


def track_offer_booked_event(user_id: int, offer: offers_models.Offer) -> None:
    event_name = BatchEvent.HAS_BOOKED_OFFER
    formatted_offer_attributes = _format_offer_attributes(offer)
    payload = TrackBatchEventRequest(event_name=event_name, event_payload=formatted_offer_attributes, user_id=user_id)
    batch_tasks.track_event_task.delay(payload)


def track_booking_cancellation(booking: bookings_models.Booking) -> None:
    from pcapi.core.users.api import get_domains_credit

    event_name = BatchEvent.RECREDIT_ACCOUNT_CANCELLATION
    user = booking.user
    offer = booking.stock.offer
    domains_credit = get_domains_credit(user)
    event_payload = {
        "credit": domains_credit.all.remaining,  # type: ignore[union-attr]
        "offer_id": offer.id,
        "offer_name": shorten_for_batch(offer.name, max_length=64, placeholder="...", preserve_words=True),
        "offer_price": booking.total_amount,
    }
    payload = TrackBatchEventRequest(event_name=event_name, event_payload=event_payload, user_id=user.id)
    batch_tasks.track_event_task.delay(payload)


def send_users_reminders_for_offer(user_ids: list[int], offer: offers_models.Offer) -> None:
    event_name = BatchEvent.FUTURE_OFFER_ACTIVATED
    formatted_offer_attributes = _format_offer_attributes(offer)

    trigger_events: list[TrackBatchEventRequest] = []
    for user_id in user_ids:
        trigger_events.append(
            TrackBatchEventRequest(event_name=event_name, event_payload=formatted_offer_attributes, user_id=user_id)
        )

    payload = TrackBatchEventsRequest(trigger_events=trigger_events)
    batch_tasks.track_event_bulk_task.delay(payload)
