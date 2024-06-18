from pcapi.connectors.apps_flyer import log_user_event
from pcapi.core.users.models import User
from pcapi.workers import worker
from pcapi.workers.decorators import job


@job(worker.default_queue)
def log_user_becomes_beneficiary_event_job(user_id: int) -> None:
    user = User.query.get(user_id)
    log_user_event(user, "af_complete_beneficiary")
