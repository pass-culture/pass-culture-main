"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/BSR-push-invoices/api/src/pcapi/scripts/push_invoices_prod/main.py

"""

import logging

from pcapi.app import app
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import models as finance_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def _push_invoices() -> None:
    invoices_query = (
        db.session.query(finance_models.Invoice)
        .filter(finance_models.Invoice.status == finance_models.InvoiceStatus.PENDING)
        .with_entities(finance_models.Invoice.id)
    )
    invoices = invoices_query.all()

    if not invoices:
        return

    invoice_ids = [e[0] for e in invoices]
    for invoice_id in invoice_ids:
        db.session.query(finance_models.Invoice).filter(finance_models.Invoice.id == invoice_id).update(
            {"status": finance_models.InvoiceStatus.PENDING_PAYMENT},
            synchronize_session=False,
        )
        # TODO We validate whether cegid succeeds in doing the payment or not for now.
        # Later, validate_invoice will only be called in case of success
        finance_api.validate_invoice(invoice_id)
        db.session.commit()


if __name__ == "__main__":
    app.app_context().push()

    _push_invoices()
