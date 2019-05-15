from scripts.payment.batch_steps import generate_new_payments
from utils.logger import logger

def create_industrial_payments():
    logger.info('create_industrial_payments')

    pending_payments, not_processable_payments = generate_new_payments()

    logger.info('created {} payments'.format(
        len(pending_payments + not_processable_payments)
    ))
