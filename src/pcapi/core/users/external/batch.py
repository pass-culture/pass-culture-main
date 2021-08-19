from datetime import datetime
import logging
from typing import Optional

from pcapi.core.users.external.models import UserAttributes
from pcapi.tasks.batch_tasks import UpdateBatchAttributesRequest
from pcapi.tasks.batch_tasks import update_user_attributes_task


logger = logging.getLogger(__name__)


BATCH_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def update_user_attributes(user_id: int, user_attributes: UserAttributes):
    if user_attributes.is_pro:
        return

    formatted_attributes = format_user_attributes(user_attributes)
    update_user_attributes_task.delay(UpdateBatchAttributesRequest(user_id=user_id, attributes=formatted_attributes))


def format_user_attributes(user_attributes: UserAttributes) -> dict:
    attributes = {
        "u.credit": int(user_attributes.domains_credit.all.remaining * 100) if user_attributes.domains_credit else None,
        "u.departement_code": user_attributes.departement_code,
        "date(u.date_of_birth)": _format_date(user_attributes.date_of_birth),
        "u.postal_code": user_attributes.postal_code,
        "date(u.date_created)": _format_date(user_attributes.date_created),
        "u.marketing_push_subscription": user_attributes.marketing_push_subscription,
        "u.is_beneficiary": user_attributes.is_beneficiary,
        "date(u.deposit_expiration_date)": _format_date(user_attributes.deposit_expiration_date),
        "date(u.last_booking_date)": _format_date(user_attributes.last_booking_date),
    }

    for product_use_date_key, product_use_date_value in user_attributes.products_use_date.items():
        attributes[f"date(u.{product_use_date_key})"] = _format_date(product_use_date_value)

    # A Batch tag can't be an empty list, otherwise the API returns an error
    if user_attributes.booking_categories:
        attributes["ut.booking_categories"] = user_attributes.booking_categories

    return attributes


def _format_date(date: Optional[datetime]) -> Optional[str]:
    return date.strftime(BATCH_DATETIME_FORMAT) if date else None
