"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=BSR-do-push-invoices \
  -f NAMESPACE=push_invoices \
  -f SCRIPT_ARGUMENTS="";

"""

import logging
import time

from pcapi import settings
from pcapi.app import app
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import conf
from pcapi.core.finance import exceptions
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.backend.cegid import INVENTORY_IDS
from pcapi.core.finance.backend.cegid import CegidFinanceBackend
from pcapi.models import db
from pcapi.notifications.internal import send_internal_message
from pcapi.scripts.pro.upload_reimbursement_csv_to_offerer_drive import export_csv_and_send_notification_emails


logger = logging.getLogger(__name__)


class MagicalCegidbackend(CegidFinanceBackend):
    def check_can_push_invoice(self) -> bool:
        return True

    def push_invoice(self, invoice: finance_models.Invoice) -> dict:
        """
        Create a new invoice.
        """
        assert invoice.bankAccountId  # helps mypy
        url = f"{self.base_url}/{self._interface}/Bill"
        params = {"$expand": "Details"}

        is_debit_note = invoice.reference.startswith("A")
        invoice_lines = self.get_invoice_lines(invoice)
        lines = [
            {
                "Amount": {"value": self._format_amount(line["amount"], is_debit_note)},
                "Branch": {"value": "PASSCULT"},
                "InventoryID": {"value": INVENTORY_IDS[line["product_id"]]},
                "TransactionDescription": {"value": line["title"]},
                "Description": {"value": line["title"]},
                "Qty": {"value": 1},
                "UnitCost": {"value": self._format_amount(line["amount"], is_debit_note)},
                "UOM": {"value": "UNITE"},
            }
            for line in invoice_lines
        ]

        total_amount_str = self._format_amount(sum(e["amount"] for e in invoice_lines), is_debit_note)
        invoice_description = self._get_formatted_invoice_description(invoice)

        body = {
            "Amount": {"value": total_amount_str},
            "ApprovedForPayment": {"value": False},
            "Balance": {"value": total_amount_str},
            "BranchID": {"value": "PASSCULT"},
            "CurrencyID": {"value": "EUR"},
            "Date": {"value": self.format_datetime(invoice.date)},
            "Description": {"value": invoice_description},  # VIRXXX - <01/12-15/12>
            "Details": lines,
            "Hold": {"value": False},
            "PostPeriod": {"value": f"{invoice.date:%m%Y}"},
            # "ReferenceNbr": {"value": invoice.reference},  # This has no effect because XRP generates an incremental ID that cannot be overriden
            "RefNbr": {"value": invoice.reference},
            "Status": {"value": "Open"},
            "TaxTotal": {"value": "0"},
            "Terms": {"value": "30J"},
            "Type": {"value": "ADR" if is_debit_note else "INV"},
            "Vendor": {"value": str(invoice.bankAccountId)},
            "VendorRef": {"value": invoice.reference},
        }

        response = self._request("PUT", url, params=params, json=body)

        if (
            response.status_code == 500
            and self._get_exception_type(response) == "PX.Api.ContractBased.OutcomeEntityHasErrorsException"
        ):
            # If the invoice is already pushed, we might be in a retry due to a timeout from the first PUT query
            # We thus get the id necessary for the POST
            logger.warning("Invoice '%s' already pushed", invoice.reference)
            response_json = self.get_invoice(invoice.reference)

        elif response.status_code != 200:
            raise exceptions.FinanceBackendBadRequest(response, "Error in invoice creation payload")

        else:
            response_json = response.json()

        if response_json.get("Status", {}).get("value") == "Balanced":
            # Set invoice to Open in Cegid
            logger.info("Set %s invoice to Open", invoice.reference)
            set_open_url = f"{self.base_url}/{self._interface}/Bill/ReleaseBill"
            set_open_response = self._request("POST", set_open_url, json={"Entity": {"id": response_json["id"]}})

            if set_open_response.status_code // 100 != 2:
                raise exceptions.FinanceBackendBadRequest(set_open_response, "Error in setting invoice to Open")

        return response_json


# Same function, using MagicalCegidbackend instead of CegidFinanceBackend
def push_invoices(count: int) -> None:
    if bool(app.redis_client.exists(conf.REDIS_PUSH_INVOICE_LOCK)):
        return

    invoices_query = (
        db.session.query(finance_models.Invoice)
        .filter(
            finance_models.Invoice.status == finance_models.InvoiceStatus.PENDING,
        )
        .with_entities(finance_models.Invoice.id)
    )
    if count != 0:
        invoices_query = invoices_query.limit(count)

    invoices = invoices_query.all()

    if not invoices:
        return

    app.redis_client.set(conf.REDIS_PUSH_INVOICE_LOCK, "1", ex=conf.REDIS_PUSH_INVOICE_LOCK_TIMEOUT)

    invoice_ids = [e[0] for e in invoices]
    encountered_error = False
    encountered_workhour = False

    try:
        for invoice_id in invoice_ids:
            try:
                backend = MagicalCegidbackend()
                logger.info("Push invoice", extra={"invoice_id": invoice_id, "backend": "MagicalCegidbackend"})
                if not backend.check_can_push_invoice():
                    logger.info(
                        "Didn't push invoice due to work hours beginning soon",
                        extra={"invoice_id": invoice_id},
                    )
                    encountered_workhour = True
                    break
                invoice = db.session.get(finance_models.Invoice, invoice_id)
                assert invoice  # helps mypy
                backend.push_invoice(invoice)
            except Exception as exc:
                logger.exception(
                    "Unable to push invoice",
                    extra={
                        "invoice_id": invoice_id,
                        "exc": str(exc),
                    },
                )
                # Wait until next cron run to continue sync process
                encountered_error = True
                break
            else:
                db.session.query(finance_models.Invoice).filter(finance_models.Invoice.id == invoice_id).update(
                    {"status": finance_models.InvoiceStatus.PENDING_PAYMENT},
                    synchronize_session=False,
                )
                # TODO We validate whether cegid succeeds in doing the payment or not for now.
                # Later, validate_invoice will only be called in case of success
                finance_api.validate_invoice(invoice_id)
                db.session.commit()
                time_to_sleep = 5
                time.sleep(time_to_sleep)

    finally:
        app.redis_client.delete(conf.REDIS_PUSH_INVOICE_LOCK)

        if not encountered_error and not encountered_workhour:
            cashflow = (
                db.session.query(finance_models.Cashflow)
                .join(finance_models.Cashflow.invoices)
                .filter(finance_models.Invoice.id.in_(invoice_ids))
                .order_by(finance_models.Invoice.id)
                .limit(1)
                .one()
            )
            batch = cashflow.batch
            if settings.GENERATE_CGR_KINEPOLIS_INVOICES:
                export_csv_and_send_notification_emails(batch.id, batch.label)

            if settings.SLACK_GENERATE_INVOICES_FINISHED_CHANNEL:
                send_internal_message(
                    channel=settings.SLACK_GENERATE_INVOICES_FINISHED_CHANNEL,
                    blocks=[
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"L'envoi des factures du ({batch.label}) sur l'outil comptable est terminé avec succès",
                            },
                        }
                    ],
                    icon_emoji=":large_green_circle:",
                )


if __name__ == "__main__":
    app.app_context().push()

    push_invoices(0)
