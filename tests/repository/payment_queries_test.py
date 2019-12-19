import uuid
from decimal import Decimal

from models import PcObject
from models.payment_status import TransactionStatus, PaymentStatus
from repository.payment_queries import find_message_checksum, find_error_payments, find_retry_payments, \
    find_payments_by_message, get_payments_by_message_id, find_not_processable_with_bank_information
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_booking, create_user, create_offerer, create_venue, create_deposit, \
    create_payment, create_payment_message, create_bank_information
from tests.model_creators.specific_creators import create_stock_from_offer, create_offer_with_thing_product


class FindMessageChecksumTest:
    @clean_database
    def test_returns_a_checksum_if_message_id_is_known(self, app):
        pass
        # given
        message_id = 'ABCD1234'
        message = create_payment_message(name=message_id)
        PcObject.save(message)

        # when
        checksum = find_message_checksum(message_id)

        # then
        assert checksum == message.checksum

    @clean_database
    def test_returns_none_is_message_id_is_unknown(self, app):
        pass
        # given
        message_id = 'ABCD1234'
        message = create_payment_message(name=message_id)
        PcObject.save(message)

        # when
        checksum = find_message_checksum('EFGH5678')

        # then
        assert checksum is None


class FindErrorPaymentsTest:
    @clean_database
    def test_returns_payments_with_last_payment_status_error(self, app):
        # Given
        user = create_user()
        booking = create_booking(user=user)
        deposit = create_deposit(user)
        error_payment1 = create_payment(booking, booking.stock.resolvedOffer.venue.managingOfferer, 10)
        error_payment2 = create_payment(booking, booking.stock.resolvedOffer.venue.managingOfferer, 10)
        pending_payment = create_payment(booking, booking.stock.resolvedOffer.venue.managingOfferer, 10)
        error_status1 = PaymentStatus()
        error_status1.status = TransactionStatus.ERROR
        error_payment1.statuses.append(error_status1)
        error_status2 = PaymentStatus()
        error_status2.status = TransactionStatus.ERROR
        error_payment2.statuses.append(error_status2)

        PcObject.save(error_payment1, error_payment2, pending_payment, deposit)

        # When
        payments = find_error_payments()

        # Then
        assert len(payments) == 2
        for p in payments:
            assert p.currentStatus.status == TransactionStatus.ERROR

    @clean_database
    def test_does_not_return_payment_if_has_status_error_but_not_last(self, app):
        # Given
        user = create_user()
        booking = create_booking(user=user)
        deposit = create_deposit(user)
        error_payment = create_payment(booking, booking.stock.resolvedOffer.venue.managingOfferer, 10)
        pending_payment = create_payment(booking, booking.stock.resolvedOffer.venue.managingOfferer, 10)
        error_status = PaymentStatus()
        error_status.status = TransactionStatus.ERROR
        sent_status = PaymentStatus()
        sent_status.status = TransactionStatus.SENT
        error_payment.statuses.extend([error_status, sent_status])

        PcObject.save(error_payment, pending_payment, deposit)

        # When
        payments = find_error_payments()

        # Then
        assert payments == []


class FindRetryPaymentsTest:
    @clean_database
    def test_returns_payments_with_last_payment_status_retry(self, app):
        # Given
        user = create_user()
        booking = create_booking(user=user)
        deposit = create_deposit(user)
        offerer = booking.stock.resolvedOffer.venue.managingOfferer
        retry_payment1 = create_payment(booking, offerer, 10)
        retry_payment2 = create_payment(booking, offerer, 10)
        pending_payment = create_payment(booking, offerer, 10, status=TransactionStatus.PENDING)
        retry_status1 = PaymentStatus()
        retry_status1.status = TransactionStatus.RETRY
        retry_payment1.statuses.append(retry_status1)
        retry_status2 = PaymentStatus()
        retry_status2.status = TransactionStatus.RETRY
        retry_payment2.statuses.append(retry_status2)

        PcObject.save(retry_payment1, retry_payment2, pending_payment, deposit)

        # When
        payments = find_retry_payments()

        # Then
        assert len(payments) == 2
        for p in payments:
            assert p.currentStatus.status == TransactionStatus.RETRY

    @clean_database
    def test_does_not_return_payment_if_has_status_retry_but_not_last(self, app):
        # Given
        user = create_user()
        booking = create_booking(user=user)
        deposit = create_deposit(user)
        payment = create_payment(booking, booking.stock.resolvedOffer.venue.managingOfferer, 10)
        payment = create_payment(booking, booking.stock.resolvedOffer.venue.managingOfferer, 10)
        pending_payment = create_payment(booking, booking.stock.resolvedOffer.venue.managingOfferer, 10)
        retry_status = PaymentStatus()
        retry_status.status = TransactionStatus.RETRY
        sent_status = PaymentStatus()
        sent_status.status = TransactionStatus.SENT
        payment.statuses.extend([retry_status, sent_status])

        PcObject.save(payment, pending_payment, deposit)

        # When
        payments = find_retry_payments()

        # Then
        assert payments == []


class FindPaymentsByMessageTest:
    @clean_database
    def test_returns_payments_matching_message(self, app):
        # given
        user = create_user()
        booking = create_booking(user=user)
        deposit = create_deposit(user)
        offerer = booking.stock.resolvedOffer.venue.managingOfferer

        transaction1 = create_payment_message(name='XML1')
        transaction2 = create_payment_message(name='XML2')
        transaction3 = create_payment_message(name='XML3')

        uuid1, uuid2, uuid3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()

        payments = [
            create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid1, payment_message=transaction1),
            create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid2, payment_message=transaction2),
            create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid1, payment_message=transaction3),
            create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid3, payment_message=transaction1),
            create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid1, payment_message=transaction1)
        ]

        PcObject.save(deposit, *payments)

        # when
        matching_payments = find_payments_by_message('XML1')

        # then
        assert len(matching_payments) == 3
        for p in matching_payments:
            assert p.paymentMessageName == 'XML1'

    @clean_database
    def test_returns_nothing_if_message_is_not_matched(self, app):
        # given
        user = create_user()
        booking = create_booking(user=user)
        deposit = create_deposit(user)
        offerer = booking.stock.resolvedOffer.venue.managingOfferer

        message1 = create_payment_message(name='XML1')
        message2 = create_payment_message(name='XML2')
        message3 = create_payment_message(name='XML3')

        uuid1, uuid2, uuid3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()

        payments = [
            create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid1, payment_message=message1),
            create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid2, payment_message=message2),
            create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid3, payment_message=message3)
        ]

        PcObject.save(deposit, *payments)

        # when
        matching_payments = find_payments_by_message('unknown message')

        # then
        assert matching_payments == []


class GeneratePayementsByMessageIdTest:
    @clean_database
    def test_only_returns_payments_with_given_message(self, app):
        # Given
        offerer = create_offerer(siren='123456789')
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        paying_stock = create_stock_from_offer(offer)
        free_stock = create_stock_from_offer(offer, price=0)
        user = create_user()
        deposit = create_deposit(user, amount=500)
        booking1 = create_booking(user=user, stock=paying_stock, venue=venue, is_used=True)
        booking2 = create_booking(user=user, stock=paying_stock, venue=venue, is_used=True)
        booking3 = create_booking(user=user, stock=paying_stock, venue=venue, is_used=True)
        booking4 = create_booking(user=user, stock=free_stock, venue=venue, is_used=True)
        payment1 = create_payment(booking1, offerer, 10, payment_message_name="ABCD123")
        payment2 = create_payment(booking2, offerer, 10, payment_message_name="EFGH456")

        PcObject.save(payment1, payment2)
        PcObject.save(deposit, booking1, booking3, booking4)

        # When
        payements_by_id = get_payments_by_message_id('ABCD123')

        # Then
        assert len(payements_by_id) == 1
        assert payements_by_id[0].paymentMessage.name == 'ABCD123'


class FindNotProcessableWithBankInformationTest:
    @clean_database
    def test_should_not_return_payments_to_retry_if_no_bank_information(self, app):
        # Given
        offerer = create_offerer(siren='123456789')
        user = create_user()
        venue = create_venue(offerer)
        stock = create_stock_from_offer(create_offer_with_thing_product(venue), price=0)
        booking = create_booking(user=user, stock=stock)
        not_processable_payment = create_payment(booking, offerer, Decimal(10),
                                                 status=TransactionStatus.NOT_PROCESSABLE,
                                                 iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
        PcObject.save(not_processable_payment)

        # When
        payments_to_retry = find_not_processable_with_bank_information()

        # Then
        assert payments_to_retry == []

    @clean_database
    def test_should_return_payment_to_retry_if_bank_information_linked_to_offerer_and_current_status_is_not_processable(self, app):
        # Given
        offerer = create_offerer(siren='123456789')
        user = create_user()
        venue = create_venue(offerer)
        stock = create_stock_from_offer(create_offer_with_thing_product(venue), price=0)
        booking = create_booking(user=user, stock=stock)
        not_processable_payment = create_payment(booking, offerer, Decimal(10),
                                                 status=TransactionStatus.NOT_PROCESSABLE,
                                                 iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
        bank_information = create_bank_information(offerer=offerer)
        PcObject.save(not_processable_payment, bank_information)

        # When
        payments_to_retry = find_not_processable_with_bank_information()

        # Then
        assert not_processable_payment in payments_to_retry

    @clean_database
    def test_should_not_return_payments_to_retry_if_bank_information_linked_to_offerer_and_current_status_is_not_not_processable(self, app):
        # Given
        offerer = create_offerer(siren='123456789')
        user = create_user()
        venue = create_venue(offerer)
        stock = create_stock_from_offer(create_offer_with_thing_product(venue), price=0)
        booking = create_booking(user=user, stock=stock)
        not_processable_payment = create_payment(booking, offerer, Decimal(10),
                                                 status=TransactionStatus.NOT_PROCESSABLE,
                                                 iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
        bank_information = create_bank_information(offerer=offerer)
        PcObject.save(not_processable_payment, bank_information)
        not_processable_payment.setStatus(TransactionStatus.SENT)
        PcObject.save(not_processable_payment)

        # When
        payments_to_retry = find_not_processable_with_bank_information()

        # Then
        assert payments_to_retry == []

    @clean_database
    def test_should_return_payment_to_retry_if_bank_information_linked_to_venue_and_current_status_is_not_processable(self, app):
        # Given
        offerer = create_offerer(siren='123456789')
        user = create_user()
        venue = create_venue(offerer)
        stock = create_stock_from_offer(create_offer_with_thing_product(venue), price=0)
        booking = create_booking(user=user, stock=stock)
        not_processable_payment = create_payment(booking, offerer, Decimal(10),
                                                 status=TransactionStatus.NOT_PROCESSABLE,
                                                 iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
        bank_information = create_bank_information(venue=venue)
        PcObject.save(not_processable_payment, bank_information)

        # When
        payments_to_retry = find_not_processable_with_bank_information()

        # Then
        assert not_processable_payment in payments_to_retry

