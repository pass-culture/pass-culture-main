from typing import List

from models import BankInformation, PcObject
from models.payment_status import TransactionStatus
from repository import payment_queries


def retry_linked_payments(bank_information_list: List[BankInformation]):
    payments = []
    for bank_information in bank_information_list:
        payments += payment_queries.find_all_with_status_not_processable_for_bank_information(bank_information)
    for payment in payments:
        payment.setStatus(TransactionStatus.RETRY)
    if payments:
        PcObject.check_and_save(*payments)