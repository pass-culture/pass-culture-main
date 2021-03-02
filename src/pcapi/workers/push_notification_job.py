from rq.decorators import job

from pcapi.notifications.push import update_user_attributes
from pcapi.workers import worker
from pcapi.workers.decorators import job_context
from pcapi.workers.decorators import log_job


@job(worker.default_queue, connection=worker.conn)
@job_context
@log_job
def update_user_attributes_job(user_id: int, attribute_values: dict) -> None:
    update_user_attributes(user_id, attribute_values)
