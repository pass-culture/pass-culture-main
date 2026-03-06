import logging
from datetime import datetime
from functools import partial

from pcapi.core.cultural_survey import models as cultural_survey_models
from pcapi.core.external.attributes import models as attributes_models
from pcapi.core.external.batch.utils import format_date
from pcapi.tasks import batch_tasks
from pcapi.utils.transaction_manager import on_commit

from .serialization import UpdateBatchAttributesRequest


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
    payload = UpdateBatchAttributesRequest(attributes=formatted_attributes, user_id=user_id)

    on_commit(partial(batch_tasks.update_user_attributes_android_task.delay, payload))
    on_commit(partial(batch_tasks.update_user_attributes_ios_task.delay, payload))


def format_user_attributes(
    user_attributes: attributes_models.UserAttributes,
    cultural_survey_answers: dict[str, list[str]] | None = None,
    batch_extra_data: dict[str, datetime] | None = None,
) -> dict:
    # https://doc.batch.com/api/custom-data-api/set-update/#post-data
    attributes = {
        "date(u.date_created)": format_date(user_attributes.date_created),
        "date(u.date_of_birth)": format_date(user_attributes.date_of_birth),
        "date(u.deposit_activation_date)": format_date(user_attributes.deposit_activation_date),
        "date(u.deposit_expiration_date)": format_date(user_attributes.deposit_expiration_date),
        "date(u.last_booking_date)": format_date(user_attributes.last_booking_date),
        "u.bonification_status": (
            user_attributes.bonification_status.value if user_attributes.bonification_status else None
        ),
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
        attributes[f"date(u.{product_use_date_key})"] = format_date(product_use_date_value)

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
        attributes["date(u.last_status_update_date)"] = format_date(batch_extra_data["last_status_update_date"])

    if user_attributes.achievements:
        attributes["ut.achievements"] = user_attributes.achievements

    return attributes
