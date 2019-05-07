import uuid
from datetime import datetime

import pytest

from models import PcObject
from models.payment_status import TransactionStatus
from scripts.payment.banishment import do_ban_payments, parse_raw_payments_ids
from tests.conftest import clean_database
from tests.test_utils import create_payment, create_payment_transaction, create_deposit, create_booking, create_user


@pytest.mark.standalone
class ParseRawPaymentIdsTest:
    def test_returns_a_list_of_integers(self):
        # given
        raw_ids = '111,222,333'

        # when
        ids = parse_raw_payments_ids(raw_ids)

        # then
        assert ids == [111, 222, 333]

    def test_raises_an_exception_if_integers_are_not_separated_by_commas(self):
        # given
        raw_ids = '111-222-333'

        # when
        with pytest.raises(ValueError):
            parse_raw_payments_ids(raw_ids)


@pytest.mark.standalone
class DoBanPaymentsTest:
    @clean_database
    def test_modify_statuses_on_given_payments(self, app):
        # given
        user = create_user()
        booking = create_booking(user)
        deposit = create_deposit(user, datetime.utcnow())
        offerer = booking.stock.resolvedOffer.venue.managingOfferer

        transaction1 = create_payment_transaction(transaction_message_id='XML1')
        transaction2 = create_payment_transaction(transaction_message_id='XML2')
        transaction3 = create_payment_transaction(transaction_message_id='XML3')

        uuid1, uuid2, uuid3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()

        payment1 = create_payment(booking, offerer, 5, transaction_end_ot_end_id=uuid1, transaction=transaction1)
        payment2 = create_payment(booking, offerer, 5, transaction_end_ot_end_id=uuid2, transaction=transaction2)
        payment3 = create_payment(booking, offerer, 5, transaction_end_ot_end_id=uuid1, transaction=transaction3)
        payment4 = create_payment(booking, offerer, 5, transaction_end_ot_end_id=uuid3, transaction=transaction1)
        payment5 = create_payment(booking, offerer, 5, transaction_end_ot_end_id=uuid1, transaction=transaction1)
        payment6 = create_payment(booking, offerer, 5, transaction_end_ot_end_id=uuid1, transaction=transaction1)

        PcObject.check_and_save(deposit, payment1, payment2, payment3, payment4, payment5, payment6)
        print(uuid1.hex)

        # when
        do_ban_payments('XML1', uuid1.hex, [payment1.id, payment5.id])

        # then
        assert payment1.currentStatus.status == TransactionStatus.BANNED
        assert payment2.currentStatus.status == TransactionStatus.PENDING
        assert payment3.currentStatus.status == TransactionStatus.PENDING
        assert payment4.currentStatus.status == TransactionStatus.PENDING
        assert payment5.currentStatus.status == TransactionStatus.BANNED
        assert payment6.currentStatus.status == TransactionStatus.RETRY
