import datetime
import logging

from pcapi.scripts.payment.batch_steps import generate_new_payments


logger = logging.getLogger(__name__)


def create_industrial_payments():
    logger.info("create_industrial_payments")

    cutoff_date = datetime.datetime.utcnow()
    batch_date = cutoff_date
    generate_new_payments(cutoff_date, batch_date)

    logger.info("created payments")
