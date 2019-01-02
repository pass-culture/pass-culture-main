import pytest

from models import PcObject
from repository.payment_queries import find_transaction_checksum
from tests.conftest import clean_database
from utils.test_utils import create_payment_transaction


@pytest.mark.standalone
class FindTransactionChecksumTest:
    @clean_database
    def test_returns_a_checksum_if_message_id_is_known(self, app):
        pass
        # given
        message_id = 'ABCD1234'
        transaction = create_payment_transaction(transaction_message_id=message_id)
        PcObject.check_and_save(transaction)

        # when
        checksum = find_transaction_checksum(message_id)

        # then
        assert checksum == transaction.checksum

    @clean_database
    def test_returns_none_is_message_id_is_unknown(self, app):
        pass
        # given
        message_id = 'ABCD1234'
        transaction = create_payment_transaction(transaction_message_id=message_id)
        PcObject.check_and_save(transaction)

        # when
        checksum = find_transaction_checksum('EFGH5678')

        # then
        assert checksum is None
