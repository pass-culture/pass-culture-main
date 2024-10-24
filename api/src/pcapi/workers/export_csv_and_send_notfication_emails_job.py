from pcapi.scripts.pro.upload_reimbursement_csv_to_offerer_drive import export_csv_and_send_notfication_emails
from pcapi.workers import worker
from pcapi.workers.decorators import job


@job(worker.low_queue)
def export_csv_and_send_notfication_emails_job(batch_id: int) -> None:
    export_csv_and_send_notfication_emails(batch_id)
