import uuid

import pytest

import pcapi.core.users.factories as users_factories
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_payment
from pcapi.model_creators.generic_creators import create_payment_message
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository import repository
from pcapi.scripts.payment.banishment import do_ban_payments
from pcapi.scripts.payment.banishment import parse_raw_payments_ids


class ParseRawPaymentIdsTest:
    def test_returns_a_list_of_integers(self):
        # given
        raw_ids = "111,222,333"

        # when
        ids = parse_raw_payments_ids(raw_ids)

        # then
        assert ids == [111, 222, 333]

    def test_raises_an_exception_if_integers_are_not_separated_by_commas(self):
        # given
        raw_ids = "111-222-333"

        # when
        with pytest.raises(ValueError):
            parse_raw_payments_ids(raw_ids)


class DoBanPaymentsTest:
    @pytest.mark.usefixtures("db_session")
    def test_modify_statuses_on_given_payments(self, app):
        # given
        user = users_factories.BeneficiaryFactory()
        booking = create_booking(user=user)
        offerer = booking.stock.offer.venue.managingOfferer

        transaction1 = create_payment_message(name="XML1")
        transaction2 = create_payment_message(name="XML2")
        transaction3 = create_payment_message(name="XML3")

        uuid1, uuid2, uuid3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()

        payment1 = create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid1, payment_message=transaction1)
        payment2 = create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid2, payment_message=transaction2)
        payment3 = create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid1, payment_message=transaction3)
        payment4 = create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid3, payment_message=transaction1)
        payment5 = create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid1, payment_message=transaction1)
        payment6 = create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid1, payment_message=transaction1)

        repository.save(payment1, payment2, payment3, payment4, payment5, payment6)

        # when
        do_ban_payments("XML1", [payment1.id, payment5.id])

        # then
        assert payment1.currentStatus.status == TransactionStatus.BANNED
        assert payment2.currentStatus.status == TransactionStatus.PENDING
        assert payment3.currentStatus.status == TransactionStatus.PENDING
        assert payment4.currentStatus.status == TransactionStatus.RETRY
        assert payment5.currentStatus.status == TransactionStatus.BANNED
        assert payment6.currentStatus.status == TransactionStatus.RETRY

    @pytest.mark.usefixtures("db_session")
    def test_does_not_modify_statuses_on_given_payments_if_a_payment_id_is_not_found(self, app):
        # given
        user = users_factories.BeneficiaryFactory()
        booking = create_booking(user=user)
        offerer = booking.stock.offer.venue.managingOfferer

        transaction1 = create_payment_message(name="XML1")
        transaction2 = create_payment_message(name="XML2")

        uuid1, uuid2 = uuid.uuid4(), uuid.uuid4()

        payment1 = create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid1, payment_message=transaction1)
        payment2 = create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid2, payment_message=transaction2)

        repository.save(payment1, payment2)

        # when
        do_ban_payments("XML1", [payment1.id, 123456])

        # then
        assert payment1.currentStatus.status == TransactionStatus.PENDING
        assert payment2.currentStatus.status == TransactionStatus.PENDING
