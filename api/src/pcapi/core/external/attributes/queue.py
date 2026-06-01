import logging

import redis
from flask import current_app

from pcapi.core.external.attributes.api import get_pro_attributes
from pcapi.core.external.beamer.api import update_beamer_user
from pcapi.core.external.brevo import update_contact_attributes as update_brevo_user
from pcapi.models.feature import FeatureToggle
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)

REDIS_BACKUP_EMAIL_TO_UPDATE = "pcapi:core:external:attributes:update_pro_attributes:backup"
REDIS_BACKUP_EMAIL_TO_UPDATE_TIMEOUT = 60 * 60 * 48  # 48h
REDIS_EMAIL_LIST_ATTRIBUTES_TO_UPDATE = "pcapi:core:external:attributes:update_pro_attributes:pending"


def add_email_to_async_pro_attributes_update(email: str) -> None:
    try:
        current_app.redis_client.sadd(REDIS_EMAIL_LIST_ATTRIBUTES_TO_UPDATE, email)
    except redis.exceptions.RedisError:
        logger.exception(
            "Could not add email to update queue",
            extra={"email": email, "queue": REDIS_EMAIL_LIST_ATTRIBUTES_TO_UPDATE},
        )


def update_pro_attributes() -> None:
    redis_client = current_app.redis_client
    backup_email = redis_client.get(REDIS_BACKUP_EMAIL_TO_UPDATE)
    if backup_email:
        redis_client.sadd(REDIS_EMAIL_LIST_ATTRIBUTES_TO_UPDATE, backup_email)
        redis_client.delete(REDIS_BACKUP_EMAIL_TO_UPDATE)

    while len(redis_client.smembers(REDIS_EMAIL_LIST_ATTRIBUTES_TO_UPDATE)) > 0:
        with atomic():
            email = redis_client.spop(REDIS_EMAIL_LIST_ATTRIBUTES_TO_UPDATE)
            if email:
                redis_client.set(REDIS_BACKUP_EMAIL_TO_UPDATE, email, ex=REDIS_BACKUP_EMAIL_TO_UPDATE_TIMEOUT)
                logger.info("update_pro_attributes", extra={"email": email})
                if isinstance(email, str):  # helps mypy
                    attributes = get_pro_attributes(email)
                    update_brevo_user(email, attributes, asynchronous=False)
                    if FeatureToggle.ENABLE_BEAMER.is_active():
                        update_beamer_user(attributes)
                redis_client.delete(REDIS_BACKUP_EMAIL_TO_UPDATE)
