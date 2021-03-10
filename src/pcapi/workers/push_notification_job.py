from rq.decorators import job

from pcapi.core.users.models import User
from pcapi.notifications.push import send_transactional_notification
from pcapi.notifications.push import update_user_attributes
from pcapi.notifications.push.transactional_notifications import TransactionalNotificationData
from pcapi.notifications.push.user_attributes_updates import get_user_attributes
from pcapi.workers import worker
from pcapi.workers.decorators import job_context
from pcapi.workers.decorators import log_job


@job(worker.default_queue, connection=worker.conn)
@job_context
@log_job
def update_user_attributes_job(user: User) -> None:
    update_user_attributes(user.id, get_user_attributes(user))


@job(worker.default_queue, connection=worker.conn)
@job_context
@log_job
def send_transactional_notification_job(notification_data: TransactionalNotificationData) -> None:
    send_transactional_notification(notification_data)
