"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/BSR-modify-status-in-staging/api/src/pcapi/scripts/update_staging_statuses/main.py

"""

import argparse
import datetime
import logging

from pcapi.app import app
from pcapi.core.finance import models as finance_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(not_dry: bool) -> None:
    invoices_query = db.session.query(finance_models.Invoice).filter(
        finance_models.Invoice.date > datetime.datetime(2025, 8, 31, 0, 0, 0)
    )
    invoice_ids = [invoice.id for invoice in invoices_query.all()]
    pricings_query = (
        db.session.query(finance_models.Pricing)
        .join(finance_models.Pricing.cashflows)
        .join(finance_models.Cashflow.invoices)
        .filter(finance_models.Invoice.id.in_(invoice_ids))
    )
    pricing_ids = [pricing.id for pricing in pricings_query.all()]

    db.session.query(finance_models.Pricing).filter(finance_models.Pricing.id.in_(pricing_ids)).update(
        {"status": finance_models.PricingStatus.PROCESSED}
    )
    invoices_query.update({"status": finance_models.InvoiceStatus.PENDING})


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
