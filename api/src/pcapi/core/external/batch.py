from datetime import datetime
import logging

from pcapi.core.cultural_survey import models as cultural_survey_models
from pcapi.core.external.attributes import models as attributes_models
import pcapi.core.finance.models as finance_models
import pcapi.core.fraud.models as fraud_models
import pcapi.notifications.push as push_notifications
from pcapi.tasks import batch_tasks


logger = logging.getLogger(__name__)


BATCH_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def update_user_attributes(
    user_id: int,
    user_attributes: attributes_models.UserAttributes,
    cultural_survey_answers: dict[str, list[str]] | None = None,
) -> None:
    if user_attributes.is_pro:
        return

    formatted_attributes = format_user_attributes(user_attributes, cultural_survey_answers=cultural_survey_answers)
    payload = batch_tasks.UpdateBatchAttributesRequest(attributes=formatted_attributes, user_id=user_id)

    batch_tasks.update_user_attributes_android_task.delay(payload)
    batch_tasks.update_user_attributes_ios_task.delay(payload)


def format_user_attributes(
    user_attributes: attributes_models.UserAttributes, cultural_survey_answers: dict[str, list[str]] | None = None
) -> dict:
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
        "u.marketing_push_subscription": user_attributes.marketing_push_subscription,
        "u.postal_code": user_attributes.postal_code,
        "ut.roles": user_attributes.roles if user_attributes.roles else None,
        "u.booking_count": user_attributes.booking_count,
        "u.booking_venues_count": user_attributes.booking_venues_count,
        "u.booked_offer_categories_count": len(user_attributes.booking_categories),
        "u.most_booked_subcategory": user_attributes.most_booked_subcategory,
        "u.most_booked_movie_genre": user_attributes.most_booked_movie_genre,
        "u.most_booked_music_type": user_attributes.most_booked_music_type,
        "ut.most_favorite_offer_subcat": user_attributes.most_favorite_offer_subcategories,  # max 30 char.
    }

    for product_use_date_key, product_use_date_value in user_attributes.products_use_date.items():
        attributes[f"date(u.{product_use_date_key})"] = _format_date(product_use_date_value)

    # A Batch tag can't be an empty list, otherwise the API returns an error
    if user_attributes.booking_categories:
        attributes["ut.booking_categories"] = user_attributes.booking_categories
    if user_attributes.booking_subcategories:
        attributes["ut.booking_subcategories"] = user_attributes.booking_subcategories

    if cultural_survey_answers:
        attributes.update(
            {
                "ut.intended_categories": cultural_survey_answers.get(
                    cultural_survey_models.CulturalSurveyQuestionEnum.PROJECTIONS.value, []
                )
            }
        )

    return attributes


def _format_date(date: datetime | None) -> str | None:
    return date.strftime(BATCH_DATETIME_FORMAT) if date else None


def track_deposit_activated_event(user_id: int, deposit: finance_models.Deposit) -> None:
    event_name = push_notifications.BatchEvent.USER_DEPOSIT_ACTIVATED.value
    event_payload = {"deposit_type": deposit.type.value, "deposit_amount": round(deposit.amount)}
    payload = batch_tasks.TrackBatchEventRequest(event_name=event_name, event_payload=event_payload, user_id=user_id)
    batch_tasks.track_event_task.delay(payload)


def track_identity_check_started_event(user_id: int, fraud_check_type: fraud_models.FraudCheckType) -> None:
    event_name = push_notifications.BatchEvent.USER_IDENTITY_CHECK_STARTED.value
    payload = batch_tasks.TrackBatchEventRequest(
        event_name=event_name, event_payload={"type": fraud_check_type.value}, user_id=user_id
    )
    batch_tasks.track_event_task.delay(payload)


def bulk_track_ubble_ko_events(users_per_code: dict[fraud_models.FraudReasonCode, list[int]]) -> None:
    event_name = push_notifications.BatchEvent.HAS_UBBLE_KO_STATUS
    for reason_code, user_ids in users_per_code.items():
        payload = batch_tasks.TrackBatchBulkEventRequest(
            event_name=event_name, event_payload={"error_code": reason_code.value}, user_ids=user_ids
        )
        batch_tasks.bulk_track_events_task.delay(payload)
