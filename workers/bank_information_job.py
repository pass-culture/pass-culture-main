import os
from rq.decorators import job

from workers import worker
from workers.decorators import job_context
from infrastructure.container import save_offerer_bank_informations, save_venue_bank_informations


@job(worker.redis_queue, connection=worker.conn)
@job_context
def bank_information_job(application_id: str, refferer_type: str):
    if refferer_type == 'offerer':
        save_offerer_bank_informations.execute(application_id)
    elif refferer_type == 'venue':
        save_venue_bank_informations.execute(application_id)
