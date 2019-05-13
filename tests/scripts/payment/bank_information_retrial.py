import pytest

from models import PcObject, Payment
from models.payment_status import TransactionStatus
from scripts import clean_database
from scripts.payment.bank_information_retrial import retry_linked_payments
from tests.test_utils import create_offerer, create_venue, create_bank_information, create_user, \
    create_offer_with_thing_product, create_stock, create_booking, create_payment


@pytest.mark.standalone
class RetryLinkedPaymentsTest:
    @clean_database
    def test_changes_transaction_status_to_retry_when_finds_relevant_payments(self, app):
        # Given
        offerer = create_offerer()
        other_offerer = create_offerer(siren='987654321')
        venue = create_venue(offerer, siret=offerer.siren + '12345')
        other_venue = create_venue(other_offerer, siret=other_offerer.siren + '12345')
        bank_information_list = [
            create_bank_information(offerer=offerer, id_at_providers=offerer.siren),
            create_bank_information(venue=other_venue, id_at_providers=other_venue.siret)
        ]

        user = create_user(email='1@email.com')
        offer = create_offer_with_thing_product(venue)
        other_offer = create_offer_with_thing_product(other_venue)
        stock = create_stock(offer=offer, price=0)
        other_stock = create_stock(offer=other_offer, price=0)
        booking = create_booking(user, stock, other_venue)
        other_booking = create_booking(user, other_stock, other_venue)
        payment = create_payment(booking, offerer, 10)
        other_payment = create_payment(other_booking, other_offerer, 10)
        payment.setStatus(TransactionStatus.NOT_PROCESSABLE)
        other_payment.setStatus(TransactionStatus.NOT_PROCESSABLE)

        PcObject.check_and_save(*(bank_information_list + [payment, other_payment]))

        # When
        retry_linked_payments(bank_information_list)

        # Then
        payments = Payment.query.all()
        assert len(payments) == 2
        for payment in payments:
            assert payment.currentStatus.status == TransactionStatus.RETRY

    @clean_database
    def test_does_not_call_check_and_save_if_no_relevant_payments(self, app):
        # Given
        offerer = create_offerer()
        other_offerer = create_offerer(siren='987654321')
        venue = create_venue(offerer, siret=offerer.siren + '12345')
        other_venue = create_venue(other_offerer, siret=other_offerer.siren + '12345')
        bank_information_list = [
            create_bank_information(offerer=offerer, id_at_providers=offerer.siren),
            create_bank_information(venue=other_venue, id_at_providers=other_venue.siret)
        ]

        PcObject.check_and_save(*bank_information_list)

        try:
            # When
            retry_linked_payments(bank_information_list)

        # Then
        except ValueError:
            assert pytest.fail("Should not try to save empty list")
