import logging

from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.core.external.batch import api
from pcapi.core.external.batch.serialization import TransactionalNotificationData


logger = logging.getLogger(__name__)


@celery_async_task(name="tasks.batch.priority.send_notification_data", model=TransactionalNotificationData)
def send_transactional_notification_task(payload: TransactionalNotificationData) -> None:
    api.send_transactional_notification(payload)
