from pcapi.infrastructure.worker_container import save_venue_bank_informations
from pcapi.workers import worker
from pcapi.workers.decorators import job


@job(worker.default_queue)
def bank_information_job(application_id: str, procedure_id: str) -> None:
    save_venue_bank_informations.execute(application_id, procedure_id)
