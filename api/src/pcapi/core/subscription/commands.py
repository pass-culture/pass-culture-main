import logging
import typing

import pcapi.connectors.big_query.queries.users_that_landed_on_come_back_later as big_query_queries
import pcapi.core.fraud.models as fraud_models
from pcapi.core.mails.transactional.users.ubble import reminder_emails
import pcapi.notifications.push as push_notifications
from pcapi.scheduled_tasks.decorators import log_cron_with_transaction
from pcapi.tasks import batch_tasks
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("send_beneficiary_subscription_reminders")
@log_cron_with_transaction
def send_beneficiary_subscription_reminders() -> None:
    reminder_emails.send_reminder_emails()


@blueprint.cli.command("send_reminders_to_users_that_landed_on_come_back_later")
@log_cron_with_transaction
def send_reminders_to_users_that_landed_on_come_back_later() -> None:
    _send_notification_to_users_that_landed_on_come_back_later()


def _send_notification_to_users_that_landed_on_come_back_later() -> None:
    users: typing.Iterator[
        big_query_queries.UserThatLandedOnComeBackLaterModel
    ] = big_query_queries.UsersThatLandedOnComeBackLater(days_ago=3).execute()

    # filter out users that have an identity fraud check after the event date
    users_to_notify = [
        user.user_id
        for user in users
        if fraud_models.BeneficiaryFraudCheck.query.filter(
            fraud_models.BeneficiaryFraudCheck.userId == user.user_id,
            fraud_models.BeneficiaryFraudCheck.type.in_(fraud_models.IDENTITY_CHECK_TYPES),
            fraud_models.BeneficiaryFraudCheck.dateCreated > user.event_date,
        ).count()
        == 0
    ]

    batch_tasks.track_event_for_multiple_users_task.delay(
        batch_tasks.BulkTrackBatchEventRequest(
            user_ids=users_to_notify,
            event_name=push_notifications.BatchEvent.USER_LANDED_ON_COME_BACK_LATER_PAGE,
            event_payload={"days_ago": 3},
        )
    )
