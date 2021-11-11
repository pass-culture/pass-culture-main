from pcapi.use_cases.create_beneficiary_from_application import create_beneficiary_from_application
from pcapi.workers import worker
from pcapi.workers.decorators import job


@job(worker.id_check_queue)
def beneficiary_job(
    application_id: int,
    run_fraud_detection: bool = True,
    ignore_id_piece_number_field: bool = False,
    fraud_detection_ko: bool = False,
) -> None:
    create_beneficiary_from_application.execute(
        application_id,
        run_fraud_detection=run_fraud_detection,
        ignore_id_piece_number_field=ignore_id_piece_number_field,
        fraud_detection_ko=fraud_detection_ko,
    )
