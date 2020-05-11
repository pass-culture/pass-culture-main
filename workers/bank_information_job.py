import os
from rq.decorators import job

from workers import worker
from workers.decorators import job_context
from use_cases.save_bank_informations import save_offerer_bank_informations, save_venue_bank_informations


@job(worker.redis_queue, connection=worker.conn)
@job_context
def bank_information_job(application_id: str, provider_name: str):
    if provider_name == 'offerer':
        save_offerer_bank_informations(application_id)
    elif provider_name == 'venue':
        save_venue_bank_informations(application_id)
