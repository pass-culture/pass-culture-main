from pcapi.infrastructure.worker_container import save_offerer_bank_informations
from pcapi.infrastructure.worker_container import save_venue_bank_informations
from pcapi.workers import worker
from pcapi.workers.decorators import job


@job(worker.default_queue)
def bank_information_job(application_id: str, refferer_type: str, procedure_id: str):  # type: ignore [no-untyped-def]
    if refferer_type == "offerer":
        save_offerer_bank_informations.execute(application_id)
    elif refferer_type == "venue":
        save_venue_bank_informations.execute(application_id, procedure_id)
