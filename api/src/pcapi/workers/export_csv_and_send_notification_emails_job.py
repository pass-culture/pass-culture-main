from pcapi.scripts.pro.upload_reimbursement_csv_to_offerer_drive import export_csv_and_send_notification_emails
from pcapi.workers import worker
from pcapi.workers.decorators import job


@job(worker.low_queue)
def export_csv_and_send_notification_emails_job(batch_id: int, batch_label: str) -> None:
    export_csv_and_send_notification_emails(batch_id, batch_label)
