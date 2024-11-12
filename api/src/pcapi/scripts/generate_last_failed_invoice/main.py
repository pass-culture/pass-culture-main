import logging

from pcapi.core.finance import api as finance_api
from pcapi.core.finance import models as finance_models
from pcapi.core.logging import log_elapsed


logger = logging.getLogger(__name__)

INVOICE_ID = 439298
BATCH_ID = 2072


def generate_invoice_pdf() -> None:
    invoice = finance_models.Invoice.query.filter(finance_models.Invoice.id == INVOICE_ID).one()
    batch = finance_models.CashflowBatch.query.filter(finance_models.CashflowBatch.id == BATCH_ID).one()
    log_extra = {"bank_account": invoice.bankAccountId}

    with log_elapsed(logger, "Generated invoice HTML", log_extra):
        invoice_html = finance_api._generate_invoice_html(invoice, batch)
    with log_elapsed(logger, "Generated and stored PDF invoice", log_extra):
        finance_api._store_invoice_pdf(invoice_storage_id=invoice.storage_object_id, invoice_html=invoice_html)


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    generate_invoice_pdf()
