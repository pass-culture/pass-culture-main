import logging

from pcapi.core.users.models import User
from pcapi.domain.admin_emails import send_suspended_fraudulent_users_email
from pcapi.scripts.suspend_fraudulent_beneficiary_users import suspend_fraudulent_beneficiary_users_by_ids
from pcapi.workers import worker
from pcapi.workers.decorators import job


logger = logging.getLogger(__name__)


@job(worker.low_queue)
def suspend_fraudulent_beneficiary_users_by_ids_job(fraudulent_users: list[int], admin_user: User) -> None:
    suspended_users_info = suspend_fraudulent_beneficiary_users_by_ids(fraudulent_users, admin_user, dry_run=False)
    send_suspended_fraudulent_users_email(
        suspended_users_info["fraudulent_users"], suspended_users_info["nb_cancelled_bookings"], admin_user.email  # type: ignore [arg-type]
    )
