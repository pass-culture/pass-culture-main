import os
from rq.decorators import job

from workers import worker
from workers.decorators import job_context, log_job
from infrastructure.worker_container import create_beneficiary_from_application


@job(worker.redis_queue, connection=worker.conn)
@job_context
@log_job
def beneficiary_job(application_id: int) -> None:
    create_beneficiary_from_application.execute(application_id)
