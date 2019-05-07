from typing import List

from domain.payments import apply_banishment
from models import PcObject
from repository.payment_queries import find_payments_by_transaction_and_message
from utils.logger import logger


def parse_raw_payments_ids(raw_ids: str):
    return list(map(lambda id: int(id), raw_ids.split(',')))


def do_ban_payments(message_id: str, transaction_id: str, payment_ids_to_ban: List[int]):
    matching_payments = find_payments_by_transaction_and_message(message_id, transaction_id)
    banned_payments, retry_payments = apply_banishment(matching_payments, payment_ids_to_ban)

    if banned_payments:
        PcObject.check_and_save(*(banned_payments + retry_payments))

    logger.info('Paiements bannis : %s ' % list(map(lambda p: p.id, banned_payments)))
    logger.info('Paiements à réessayer : %s ' % list(map(lambda p: p.id, retry_payments)))
