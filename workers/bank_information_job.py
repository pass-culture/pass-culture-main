from rq.decorators import job

from workers import worker
from infrastructure.worker_container import save_offerer_bank_informations, save_venue_bank_informations
from workers.decorators import log_job, \
    job_context


@job(worker.redis_queue, connection=worker.conn)
@job_context
@log_job
def bank_information_job(application_id: str, refferer_type: str):
    if refferer_type == 'offerer':
        save_offerer_bank_informations.execute(application_id)
    elif refferer_type == 'venue':
        save_venue_bank_informations.execute(application_id)
