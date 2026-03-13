import logging

from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.core.external.batch import api
from pcapi.core.external.batch.serialization import TransactionalNotificationDataV2


logger = logging.getLogger(__name__)


@celery_async_task(name="tasks.batch.priority.send_notification_data", model=TransactionalNotificationDataV2)
def send_transactional_notification_task(payload: TransactionalNotificationDataV2) -> None:
    api.send_transactional_notification(payload)
