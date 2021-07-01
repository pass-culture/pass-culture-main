from pcapi.use_cases.create_beneficiary_from_application import create_beneficiary_from_application
from pcapi.workers import worker
from pcapi.workers.decorators import job


@job(worker.id_check_queue)
def beneficiary_job(application_id: int, run_fraud_detection: bool = True, fraud_detection_ko: bool = False) -> None:
    create_beneficiary_from_application.execute(application_id, run_fraud_detection, fraud_detection_ko)
