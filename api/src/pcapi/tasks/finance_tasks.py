import logging

from flask import current_app

from pcapi import settings
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import conf as finance_conf
from pcapi.core.finance import models as finance_models
from pcapi.repository import transaction
from pcapi.routes.serialization import BaseModel
from pcapi.tasks.cloud_task import list_tasks
from pcapi.tasks.decorator import task


logger = logging.getLogger(__name__)


class GenerateInvoicePayload(BaseModel):
    bank_account_id: int
    cashflow_ids: list[int]
    batch_id: int


def is_generate_invoices_queue_empty() -> bool:
    results = list_tasks(settings.GENERATE_INVOICES_QUEUE_NAME)
    return len(results) == 0


@task(
    settings.GENERATE_INVOICES_QUEUE_NAME, "/finance/generate-store-invoice-bank-account", task_request_timeout=15 * 60
)
def generate_and_store_invoice_task(payload: GenerateInvoicePayload) -> None:
    try:
        with transaction():
            finance_api.generate_and_store_invoice(
                bank_account_id=payload.bank_account_id, cashflow_ids=payload.cashflow_ids, is_debit_note=False
            )
            logger.info("Generated and sent invoice", extra={"bank_account_id": payload.bank_account_id})

            finance_api.generate_and_store_invoice(
                bank_account_id=payload.bank_account_id, cashflow_ids=payload.cashflow_ids, is_debit_note=True
            )
            logger.info("Generated and sent debit note", extra={"bank_account_id": payload.bank_account_id})
            # When it's the last invoice, generate and upload the invoices file
            if current_app.redis_client.decr(finance_conf.REDIS_INVOICES_LEFT_TO_GENERATE) == 0:
                try:
                    batch = finance_models.CashflowBatch.query.filter_by(id=payload.batch_id).one()
                    path = finance_api.generate_invoice_file(batch)
                    logger.info("Generated CSV invoices file")
                    drive_folder_name = finance_api._get_drive_folder_name(batch)
                    finance_api._upload_files_to_google_drive(drive_folder_name, [path])
                    logger.info("Uploaded CSV invoices file to Google Drive")
                    # TODO (vroullier, 2023-10-10) send mail about successful generation

                except Exception as exc:  # pylint: disable=broad-except
                    logger.exception(
                        "Failed to generate invoices CSV file",
                        extra={"batch_id": payload.batch_id, "exception": exc},
                    )
                    # TODO (vroullier, 2023-10-10) send mail about failed generation
                current_app.redis_client.delete(finance_conf.REDIS_INVOICES_LEFT_TO_GENERATE)
                current_app.redis_client.delete(finance_conf.REDIS_GENERATE_INVOICES_LENGTH)

    except Exception as exc:  # pylint: disable=broad-except
        logger.exception(
            "Could not generate invoice",
            extra={
                "bank_account_id": payload.bank_account_id,
                "cashflow_ids": payload.cashflow_ids,
                "exc": str(exc),
            },
        )
