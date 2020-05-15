import os
from rq.decorators import job

from workers import worker
from workers.decorators import job_context
from use_cases.save_venue_bank_informations import SaveVenueBankInformations
from use_cases.save_offerer_bank_informations import SaveOffererBankInformations


@job(worker.redis_queue, connection=worker.conn)
@job_context
def bank_information_job(application_id: str, refferer_type: str):
    if refferer_type == 'offerer':
        SaveOffererBankInformations.execute(application_id)
    elif refferer_type == 'venue':
        SaveVenueBankInformations.execute(application_id)
