from decimal import Decimal
from unittest.mock import Mock

import pytest
from freezegun import freeze_time
from lxml.etree import DocumentInvalid

from models import PcObject
from models.feature import FeatureToggle
from models.payment import Payment
from models.payment_status import TransactionStatus, PaymentStatus
from scripts.payment.batch_steps import generate_new_payments, send_transactions, send_payments_details, \
    send_wallet_balances, \
    send_payments_report, concatenate_payments_with_errors_and_retries
from tests.conftest import clean_database, mocked_mail
from tests.test_utils import create_offerer, create_venue, create_offer_with_thing_product, create_stock_from_offer, \
    create_booking, create_user, create_deposit, create_payment, create_bank_information, deactivate_feature


class GenerateNewPaymentsTest:
    class WhenReimbursementByOffererTest:
        @clean_database
        def test_records_new_payment_lines_in_database(self, app):
            # Given
            deactivate_feature(FeatureToggle.REIMBURSEMENT_BY_VENUE)
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            paying_stock = create_stock_from_offer(offer)
            free_stock = create_stock_from_offer(offer, price=0)
            user = create_user()
            deposit = create_deposit(user, amount=500)
            booking1 = create_booking(user, paying_stock, venue, is_used=True)
            booking2 = create_booking(user, paying_stock, venue, is_used=True)
            booking3 = create_booking(user, paying_stock, venue, is_used=True)
            booking4 = create_booking(user, free_stock, venue, is_used=True)
            payment1 = create_payment(booking2, offerer, 10, payment_message_name="ABCD123")

            PcObject.save(payment1)
            PcObject.save(deposit, booking1, booking3, booking4)

            initial_payment_count = Payment.query.count()

            # When
            generate_new_payments()

            # Then
            assert Payment.query.count() - initial_payment_count == 2

        @clean_database
        def test_returns_a_tuple_of_pending_and_not_processable_payments(self, app):
            # Given
            deactivate_feature(FeatureToggle.REIMBURSEMENT_BY_VENUE)
            offerer1 = create_offerer(siren='123456789')
            offerer2 = create_offerer(siren='987654321')
            PcObject.save(offerer1)
            bank_information = create_bank_information(bic='BDFEFR2LCCB', iban='FR7630006000011234567890189',
                                                       id_at_providers='123456789', offerer=offerer1)
            venue1 = create_venue(offerer1, siret='12345678912345')
            venue2 = create_venue(offerer2, siret='98765432154321')
            offer1 = create_offer_with_thing_product(venue1)
            offer2 = create_offer_with_thing_product(venue2)
            paying_stock1 = create_stock_from_offer(offer1)
            paying_stock2 = create_stock_from_offer(offer2)
            free_stock1 = create_stock_from_offer(offer1, price=0)
            user = create_user()
            deposit = create_deposit(user, amount=500)
            booking1 = create_booking(user, paying_stock1, venue1, is_used=True)
            booking2 = create_booking(user, paying_stock1, venue1, is_used=True)
            booking3 = create_booking(user, paying_stock2, venue2, is_used=True)
            booking4 = create_booking(user, free_stock1, venue1, is_used=True)
            PcObject.save(deposit, booking1, booking2, booking3, booking4, bank_information)

            # When
            pending, not_processable = generate_new_payments()

            # Then
            assert len(pending) == 2
            assert len(not_processable) == 1

        @clean_database
        def test_should_not_reimburse_offerer_if_he_has_more_than_20000_euros_in_bookings_on_several_venues(self, app):
            # Given
            deactivate_feature(FeatureToggle.REIMBURSEMENT_BY_VENUE)
            offerer1 = create_offerer(siren='123456789')
            PcObject.save(offerer1)
            bank_information = create_bank_information(bic='BDFEFR2LCCB', iban='FR7630006000011234567890189',
                                                       id_at_providers='123456789', offerer=offerer1)
            venue1 = create_venue(offerer1, siret='12345678912345')
            venue2 = create_venue(offerer1, siret='98765432154321')
            venue3 = create_venue(offerer1, siret='98123432154321')
            offer1 = create_offer_with_thing_product(venue1)
            offer2 = create_offer_with_thing_product(venue2)
            offer3 = create_offer_with_thing_product(venue3)
            paying_stock1 = create_stock_from_offer(offer1, price=10000)
            paying_stock2 = create_stock_from_offer(offer2, price=10000)
            paying_stock3 = create_stock_from_offer(offer3, price=10000)
            user = create_user()
            deposit = create_deposit(user, amount=50000)
            booking1 = create_booking(user, paying_stock1, venue1, quantity=1, is_used=True)
            booking2 = create_booking(user, paying_stock2, venue2, quantity=1, is_used=True)
            booking3 = create_booking(user, paying_stock3, venue3, quantity=1, is_used=True)
            PcObject.save(deposit, booking1, booking2, booking3, bank_information)

            # When
            pending, not_processable = generate_new_payments()

            # Then
            assert len(pending) == 2
            assert len(not_processable) == 0
            assert sum(p.amount for p in pending) == 20000

    class WhenReimbursementByVenueTest:
        @clean_database
        def test_records_new_payment_lines_in_database(self, app):
            # Given
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            paying_stock = create_stock_from_offer(offer)
            free_stock = create_stock_from_offer(offer, price=0)
            user = create_user()
            deposit = create_deposit(user, amount=500)
            booking1 = create_booking(user, paying_stock, venue, is_used=True)
            booking2 = create_booking(user, paying_stock, venue, is_used=True)
            booking3 = create_booking(user, paying_stock, venue, is_used=True)
            booking4 = create_booking(user, free_stock, venue, is_used=True)
            payment1 = create_payment(booking2, offerer, 10, payment_message_name="ABCD123")

            PcObject.save(payment1)
            PcObject.save(deposit, booking1, booking3, booking4)

            initial_payment_count = Payment.query.count()

            # When
            generate_new_payments()

            # Then
            assert Payment.query.count() - initial_payment_count == 2

        @clean_database
        def test_returns_a_tuple_of_pending_and_not_processable_payments(self, app):
            # Given
            offerer1 = create_offerer(siren='123456789')
            offerer2 = create_offerer(siren='987654321')
            PcObject.save(offerer1)
            bank_information = create_bank_information(bic='BDFEFR2LCCB', iban='FR7630006000011234567890189',
                                                       id_at_providers='123456789', offerer=offerer1)
            venue1 = create_venue(offerer1, siret='12345678912345')
            venue2 = create_venue(offerer2, siret='98765432154321')
            offer1 = create_offer_with_thing_product(venue1)
            offer2 = create_offer_with_thing_product(venue2)
            paying_stock1 = create_stock_from_offer(offer1)
            paying_stock2 = create_stock_from_offer(offer2)
            free_stock1 = create_stock_from_offer(offer1, price=0)
            user = create_user()
            deposit = create_deposit(user, amount=500)
            booking1 = create_booking(user, paying_stock1, venue1, is_used=True)
            booking2 = create_booking(user, paying_stock1, venue1, is_used=True)
            booking3 = create_booking(user, paying_stock2, venue2, is_used=True)
            booking4 = create_booking(user, free_stock1, venue1, is_used=True)
            PcObject.save(deposit, booking1, booking2, booking3, booking4, bank_information)

            # When
            pending, not_processable = generate_new_payments()

            # Then
            assert len(pending) == 2
            assert len(not_processable) == 1

        @clean_database
        def test_reimburse_offerer_if_he_has_more_than_20000_euros_in_bookings_on_several_venues(self, app):
            # Given
            offerer1 = create_offerer(siren='123456789')
            PcObject.save(offerer1)
            bank_information = create_bank_information(bic='BDFEFR2LCCB', iban='FR7630006000011234567890189',
                                                       id_at_providers='123456789', offerer=offerer1)
            venue1 = create_venue(offerer1, siret='12345678912345')
            venue2 = create_venue(offerer1, siret='98765432154321')
            venue3 = create_venue(offerer1, siret='98123432154321')
            offer1 = create_offer_with_thing_product(venue1)
            offer2 = create_offer_with_thing_product(venue2)
            offer3 = create_offer_with_thing_product(venue3)
            paying_stock1 = create_stock_from_offer(offer1, price=10000)
            paying_stock2 = create_stock_from_offer(offer2, price=10000)
            paying_stock3 = create_stock_from_offer(offer3, price=10000)
            user = create_user()
            deposit = create_deposit(user, amount=50000)
            booking1 = create_booking(user, paying_stock1, venue1, quantity=1, is_used=True)
            booking2 = create_booking(user, paying_stock2, venue2, quantity=1, is_used=True)
            booking3 = create_booking(user, paying_stock3, venue3, quantity=1, is_used=True)
            PcObject.save(deposit, booking1, booking2, booking3, bank_information)

            # When
            pending, not_processable = generate_new_payments()

            # Then
            assert len(pending) == 3
            assert len(not_processable) == 0
            assert sum(p.amount for p in pending) == 30000

        @clean_database
        def test_does_not_reimburse_offerer_for_venues_with_bookings_exceeding_20000_euros(self, app):
            # Given
            offerer1 = create_offerer(siren='123456789')
            PcObject.save(offerer1)
            bank_information = create_bank_information(bic='BDFEFR2LCCB', iban='FR7630006000011234567890189',
                                                       id_at_providers='123456789', offerer=offerer1)
            venue1 = create_venue(offerer1, siret='12345678912345')
            venue2 = create_venue(offerer1, siret='98765432154321')
            venue3 = create_venue(offerer1, siret='98123432154321')
            offer1 = create_offer_with_thing_product(venue1)
            offer2 = create_offer_with_thing_product(venue2)
            offer3 = create_offer_with_thing_product(venue3)
            paying_stock1 = create_stock_from_offer(offer1, price=10000)
            paying_stock2 = create_stock_from_offer(offer2, price=10000)
            paying_stock3 = create_stock_from_offer(offer3, price=30000)
            user = create_user()
            deposit = create_deposit(user, amount=50000)
            booking1 = create_booking(user, paying_stock1, venue1, quantity=1, is_used=True)
            booking2 = create_booking(user, paying_stock2, venue2, quantity=1, is_used=True)
            booking3 = create_booking(user, paying_stock3, venue3, quantity=1, is_used=True)
            PcObject.save(deposit, booking1, booking2, booking3, bank_information)

            # When
            pending, not_processable = generate_new_payments()

            # Then
            assert len(pending) == 2
            assert len(not_processable) == 0
            assert sum(p.amount for p in pending) == 20000


class ConcatenatePaymentsWithErrorsAndRetriesTest:
    @clean_database
    def test_a_list_of_payments_is_returned_with_statuses_in_error_or_retry_or_pending(self, app):
        # Given
        user = create_user()
        booking = create_booking(user)
        deposit = create_deposit(user)
        offerer = booking.stock.resolvedOffer.venue.managingOfferer

        error_payment = create_payment(booking, offerer, 10)
        retry_payment = create_payment(booking, offerer, 10)
        pending_payment = create_payment(booking, offerer, 10)
        not_processable_payment = create_payment(booking, offerer, 10)

        error_status = PaymentStatus()
        error_status.status = TransactionStatus.ERROR
        error_payment.statuses.append(error_status)

        retry_status = PaymentStatus()
        retry_status.status = TransactionStatus.RETRY
        retry_payment.statuses.append(retry_status)

        not_processable_status = PaymentStatus()
        not_processable_status.status = TransactionStatus.NOT_PROCESSABLE
        not_processable_payment.statuses.append(not_processable_status)

        PcObject.save(error_payment, retry_payment, pending_payment, deposit)

        # When
        payments = concatenate_payments_with_errors_and_retries([pending_payment])

        # Then
        assert len(payments) == 3
        allowed_statuses = (TransactionStatus.RETRY, TransactionStatus.ERROR, TransactionStatus.PENDING)
        assert all(map(lambda p: p.currentStatus.status in allowed_statuses, payments))


@mocked_mail
@clean_database
def test_send_transactions_should_not_send_an_email_if_pass_culture_iban_is_missing(app):
    # given
    offerer1 = create_offerer(name='first offerer')
    user = create_user()
    venue1 = create_venue(offerer1)
    stock1 = create_stock_from_offer(create_offer_with_thing_product(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    payments = [
        create_payment(booking1, offerer1, Decimal(10)),
        create_payment(booking2, offerer1, Decimal(20)),
        create_payment(booking3, offerer1, Decimal(20))
    ]

    # when
    with pytest.raises(Exception) as e:
        send_transactions(payments, None, 'AZERTY9Q666', '0000', ['comptable@test.com'])

    # then
    app.mailjet_client.send.create.assert_not_called()


@mocked_mail
@clean_database
def test_send_transactions_should_not_send_an_email_if_pass_culture_bic_is_missing(app):
    # given
    offerer1 = create_offerer(name='first offerer')
    user = create_user()
    venue1 = create_venue(offerer1)
    stock1 = create_stock_from_offer(create_offer_with_thing_product(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    payments = [
        create_payment(booking1, offerer1, Decimal(10)),
        create_payment(booking2, offerer1, Decimal(20)),
        create_payment(booking3, offerer1, Decimal(20))
    ]

    # when
    with pytest.raises(Exception):
        send_transactions(payments, 'BD12AZERTY123456', None, '0000', ['comptable@test.com'])

    # then
    app.mailjet_client.send.create.assert_not_called()


@mocked_mail
@clean_database
def test_send_transactions_should_not_send_an_email_if_pass_culture_id_is_missing(app):
    # given
    offerer1 = create_offerer(name='first offerer')
    user = create_user()
    venue1 = create_venue(offerer1)
    stock1 = create_stock_from_offer(create_offer_with_thing_product(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    payments = [
        create_payment(booking1, offerer1, Decimal(10)),
        create_payment(booking2, offerer1, Decimal(20)),
        create_payment(booking3, offerer1, Decimal(20))
    ]

    # when
    with pytest.raises(Exception):
        send_transactions(payments, 'BD12AZERTY123456', 'AZERTY9Q666', None, ['comptable@test.com'])

    # then
    app.mailjet_client.send.create.assert_not_called()


@mocked_mail
@clean_database
def test_send_transactions_should_send_an_email_with_xml_attachment(app):
    # given
    offerer1 = create_offerer(name='first offerer')
    user = create_user()
    venue1 = create_venue(offerer1)
    stock1 = create_stock_from_offer(create_offer_with_thing_product(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    deposit = create_deposit(user, amount=500)
    PcObject.save(deposit)
    payments = [
        create_payment(booking1, offerer1, Decimal(10)),
        create_payment(booking2, offerer1, Decimal(20)),
        create_payment(booking3, offerer1, Decimal(20))
    ]

    app.mailjet_client.send.create.return_value = Mock(status_code=200)

    # when
    send_transactions(payments, 'BD12AZERTY123456', 'AZERTY9Q666', '0000', ['comptable@test.com'])

    # then
    app.mailjet_client.send.create.assert_called_once()
    args = app.mailjet_client.send.create.call_args
    assert len(args[1]['data']['Attachments']) == 1


@clean_database
@mocked_mail
@freeze_time('2018-10-15 09:21:34')
def test_send_transactions_creates_a_new_payment_transaction_if_email_was_sent_properly(app):
    # given@
    offerer1 = create_offerer(name='first offerer')
    user = create_user()
    venue1 = create_venue(offerer1)
    stock1 = create_stock_from_offer(create_offer_with_thing_product(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    deposit = create_deposit(user, amount=500)
    payments = [
        create_payment(booking1, offerer1, Decimal(10), iban='CF13QSDFGH456789', bic='QSDFGH8Z555'),
        create_payment(booking2, offerer1, Decimal(20), iban='CF13QSDFGH456789', bic='QSDFGH8Z555'),
        create_payment(booking3, offerer1, Decimal(20), iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
    ]

    PcObject.save(deposit)
    PcObject.save(*payments)

    app.mailjet_client.send.create.return_value = Mock(status_code=200)

    # when
    send_transactions(payments, 'BD12AZERTY123456', 'AZERTY9Q666', '0000', ['comptable@test.com'])

    # then
    updated_payments = Payment.query.all()
    assert all(p.paymentMessageName == 'passCulture-SCT-20181015-092134' for p in updated_payments)
    assert all(p.paymentMessageChecksum == payments[0].paymentMessageChecksum for p in updated_payments)


@clean_database
@mocked_mail
def test_send_transactions_set_status_to_sent_if_email_was_sent_properly(app):
    # given
    offerer1 = create_offerer(name='first offerer')
    user = create_user()
    venue1 = create_venue(offerer1)
    stock1 = create_stock_from_offer(create_offer_with_thing_product(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    deposit = create_deposit(user, amount=500)
    payments = [
        create_payment(booking1, offerer1, Decimal(10), iban='CF13QSDFGH456789', bic='QSDFGH8Z555'),
        create_payment(booking2, offerer1, Decimal(20), iban='CF13QSDFGH456789', bic='QSDFGH8Z555'),
        create_payment(booking3, offerer1, Decimal(20), iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
    ]

    PcObject.save(deposit)
    PcObject.save(*payments)

    app.mailjet_client.send.create.return_value = Mock(status_code=200)

    # when
    send_transactions(payments, 'BD12AZERTY123456', 'AZERTY9Q666', '0000', ['comptable@test.com'])

    # then
    updated_payments = Payment.query.all()
    for payment in updated_payments:
        assert len(payment.statuses) == 2
        assert payment.currentStatus.status == TransactionStatus.SENT


@clean_database
@mocked_mail
def test_send_transactions_set_status_to_error_with_details_if_email_was_not_sent_properly(
        app):
    # given
    offerer1 = create_offerer(name='first offerer')
    user = create_user()
    venue1 = create_venue(offerer1)
    stock1 = create_stock_from_offer(create_offer_with_thing_product(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    deposit = create_deposit(user, amount=500)
    payments = [
        create_payment(booking1, offerer1, Decimal(10), iban='CF13QSDFGH456789', bic='QSDFGH8Z555'),
        create_payment(booking2, offerer1, Decimal(20), iban='CF13QSDFGH456789', bic='QSDFGH8Z555'),
        create_payment(booking3, offerer1, Decimal(20), iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
    ]

    PcObject.save(deposit)
    PcObject.save(*payments)

    app.mailjet_client.send.create.return_value = Mock(status_code=400)

    # when
    send_transactions(payments, 'BD12AZERTY123456', 'AZERTY9Q666', '0000', ['comptable@test.com'])

    # then
    updated_payments = Payment.query.all()
    for payment in updated_payments:
        assert len(payment.statuses) == 2
        assert payment.currentStatus.status == TransactionStatus.ERROR
        assert payment.currentStatus.detail == "Erreur d'envoi à MailJet"


@clean_database
@mocked_mail
def test_send_transactions_with_malformed_iban_on_payments_gives_them_an_error_status_with_a_cause(
        app):
    # given
    offerer = create_offerer(name='first offerer')
    user = create_user()
    venue = create_venue(offerer)
    stock = create_stock_from_offer(create_offer_with_thing_product(venue))
    booking = create_booking(user, stock)
    deposit = create_deposit(user, amount=500)
    payments = [
        create_payment(booking, offerer, Decimal(10), iban='CF  13QSDFGH45 qbc //', bic='QSDFGH8Z555'),
    ]

    PcObject.save(deposit, *payments)
    app.mailjet_client.send.create.return_value = Mock(status_code=400)

    # when
    with pytest.raises(DocumentInvalid):
        send_transactions(payments, 'BD12AZERTY123456', 'AZERTY9Q666', '0000', ['comptable@test.com'])

    # then
    updated_payments = Payment.query.all()
    for payment in updated_payments:
        assert len(payment.statuses) == 2
        assert payment.currentStatus.status == TransactionStatus.NOT_PROCESSABLE
        assert payment.currentStatus.detail == "Element '{urn:iso:std:iso:20022:tech:xsd:pain.001.001.03}IBAN': " \
                                               "[facet 'pattern'] The value 'CF  13QSDFGH45 qbc //' is not accepted " \
                                               "by the pattern '[A-Z]{2,2}[0-9]{2,2}[a-zA-Z0-9]{1,30}'., line 76"


@clean_database
@mocked_mail
def test_send_payment_details_sends_a_csv_attachment(app):
    # given
    offerer1 = create_offerer(name='first offerer')
    user = create_user()
    venue1 = create_venue(offerer1)
    stock1 = create_stock_from_offer(create_offer_with_thing_product(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    deposit = create_deposit(user, amount=500)
    payments = [
        create_payment(booking1, offerer1, Decimal(10), iban='CF13QSDFGH456789', bic='QSDFGH8Z555'),
        create_payment(booking2, offerer1, Decimal(20), iban='CF13QSDFGH456789', bic='QSDFGH8Z555'),
        create_payment(booking3, offerer1, Decimal(20), iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
    ]

    PcObject.save(deposit)
    PcObject.save(*payments)

    app.mailjet_client.send.create.return_value = Mock(status_code=200)

    # when
    send_payments_details(payments, ['comptable@test.com'])

    # then
    app.mailjet_client.send.create.assert_called_once()
    args = app.mailjet_client.send.create.call_args
    assert len(args[1]['data']['Attachments']) == 1
    assert args[1]['data']['Attachments'][0]['ContentType'] == 'text/csv'


@mocked_mail
def test_send_payment_details_does_not_send_anything_if_all_payment_have_error_status(app):
    # given
    offerer1 = create_offerer(name='first offerer')
    user = create_user()
    venue1 = create_venue(offerer1)
    stock1 = create_stock_from_offer(create_offer_with_thing_product(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)

    payments = [
        create_payment(booking1, offerer1, Decimal(10), status=TransactionStatus.ERROR, iban='CF13QSDFGH456789',
                       bic='QSDFGH8Z555'),
        create_payment(booking2, offerer1, Decimal(20), status=TransactionStatus.ERROR, iban='CF13QSDFGH456789',
                       bic='QSDFGH8Z555'),
        create_payment(booking3, offerer1, Decimal(20), status=TransactionStatus.ERROR, iban='CF13QSDFGH456789',
                       bic='QSDFGH8Z555')
    ]

    # when
    send_payments_details(payments, ['comptable@test.com'])

    # then
    app.mailjet_client.send.create.assert_not_called()


@mocked_mail
def test_send_payment_details_does_not_send_anything_if_recipients_are_missing(app):
    # given
    payments = []

    # when
    with pytest.raises(Exception):
        send_payments_details(payments, None)

    # then
    app.mailjet_client.send.create.assert_not_called()


@clean_database
@mocked_mail
def test_send_wallet_balances_sends_a_csv_attachment(app):
    # given
    app.mailjet_client.send.create.return_value = Mock(status_code=200)

    # when
    send_wallet_balances(['comptable@test.com'])

    # then
    app.mailjet_client.send.create.assert_called_once()
    args = app.mailjet_client.send.create.call_args
    assert len(args[1]['data']['Attachments']) == 1
    assert args[1]['data']['Attachments'][0]['ContentType'] == 'text/csv'


@mocked_mail
def test_send_wallet_balances_does_not_send_anything_if_recipients_are_missing(app):
    # when
    with pytest.raises(Exception):
        send_wallet_balances(None)

    # then
    app.mailjet_client.send.create.assert_not_called()


@mocked_mail
@clean_database
def test_send_payments_report_sends_two_csv_attachments_if_some_payments_are_not_processable_and_in_error(app):
    # given
    offerer1 = create_offerer(name='first offerer')
    user = create_user()
    venue1 = create_venue(offerer1)
    stock1 = create_stock_from_offer(create_offer_with_thing_product(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    deposit = create_deposit(user, amount=500)
    payments = [
        create_payment(booking1, offerer1, Decimal(10), status=TransactionStatus.SENT, iban='CF13QSDFGH456789',
                       bic='QSDFGH8Z555'),
        create_payment(booking2, offerer1, Decimal(20), status=TransactionStatus.ERROR, iban='CF13QSDFGH456789',
                       bic='QSDFGH8Z555'),
        create_payment(booking3, offerer1, Decimal(20), status=TransactionStatus.NOT_PROCESSABLE,
                       iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
    ]

    PcObject.save(deposit)
    PcObject.save(*payments)

    app.mailjet_client.send.create.return_value = Mock(status_code=200)

    # when
    send_payments_report(payments, ['dev.team@test.com'])

    # then
    app.mailjet_client.send.create.assert_called_once()
    args = app.mailjet_client.send.create.call_args
    assert len(args[1]['data']['Attachments']) == 2
    assert args[1]['data']['Attachments'][0]['ContentType'] == 'text/csv'
    assert args[1]['data']['Attachments'][1]['ContentType'] == 'text/csv'


@mocked_mail
@clean_database
def test_send_payments_report_sends_two_csv_attachments_if_no_payments_are_in_error_or_sent(app):
    # given
    offerer1 = create_offerer(name='first offerer')
    user = create_user()
    venue1 = create_venue(offerer1)
    stock1 = create_stock_from_offer(create_offer_with_thing_product(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    deposit = create_deposit(user, amount=500)
    payments = [
        create_payment(booking1, offerer1, Decimal(10), status=TransactionStatus.SENT, iban='CF13QSDFGH456789',
                       bic='QSDFGH8Z555'),
        create_payment(booking2, offerer1, Decimal(20), status=TransactionStatus.SENT, iban='CF13QSDFGH456789',
                       bic='QSDFGH8Z555'),
        create_payment(booking3, offerer1, Decimal(20), status=TransactionStatus.SENT, iban='CF13QSDFGH456789',
                       bic='QSDFGH8Z555')
    ]

    PcObject.save(deposit)
    PcObject.save(*payments)

    app.mailjet_client.send.create.return_value = Mock(status_code=200)

    # when
    send_payments_report(payments, ['dev.team@test.com'])

    # then
    app.mailjet_client.send.create.assert_called_once()
    args = app.mailjet_client.send.create.call_args
    assert len(args[1]['data']['Attachments']) == 2
    assert args[1]['data']['Attachments'][0]['ContentType'] == 'text/csv'
    assert args[1]['data']['Attachments'][1]['ContentType'] == 'text/csv'


@mocked_mail
@clean_database
def test_send_payments_report_does_not_send_anything_if_no_payments_are_provided(app):
    # given
    payments = []

    # when
    send_payments_report(payments, ['dev.team@test.com'])

    # then
    app.mailjet_client.send.create.assert_not_called()
