import pytest
from datetime import datetime
from decimal import Decimal
from freezegun import freeze_time
from unittest.mock import Mock

from models import PcObject
from models.payment import Payment
from models.payment_status import TransactionStatus
from scripts.payments import generate_new_payments, send_transactions, send_payments_details, send_wallet_balances, \
    send_payments_report
from tests.conftest import clean_database, mocked_mail
from tests.test_utils import create_offerer, create_venue, create_thing_offer, create_stock_from_offer, \
    create_booking, create_user, create_deposit, create_payment, create_bank_information


@pytest.mark.standalone
@clean_database
def test_generate_new_payments_records_new_payment_lines_in_database(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_thing_offer(venue)
    paying_stock = create_stock_from_offer(offer)
    free_stock = create_stock_from_offer(offer, price=0)
    user = create_user()
    deposit = create_deposit(user, datetime.utcnow(), amount=500)
    booking1 = create_booking(user, paying_stock, venue, is_used=True)
    booking2 = create_booking(user, paying_stock, venue, is_used=True)
    booking3 = create_booking(user, paying_stock, venue, is_used=True)
    booking4 = create_booking(user, free_stock, venue, is_used=True)
    payment1 = create_payment(booking2, offerer, 10, transaction_message_id="ABCD123")

    PcObject.check_and_save(payment1)
    PcObject.check_and_save(deposit, booking1, booking3, booking4)

    initial_payment_count = Payment.query.count()

    # When
    generate_new_payments()

    # Then
    assert Payment.query.count() - initial_payment_count == 2


@pytest.mark.standalone
@clean_database
def test_generate_new_payments_returns_a_tuple_of_pending_and_not_processable_payments(app):
    # Given
    offerer1 = create_offerer(siren='123456789')
    offerer2 = create_offerer(siren='987654321')
    PcObject.check_and_save(offerer1)
    bank_information = create_bank_information(bic='BDFEFR2LCCB', iban='FR7630006000011234567890189',
                                               id_at_providers='123456789', offerer=offerer1)
    venue1 = create_venue(offerer1, siret='12345678912345')
    venue2 = create_venue(offerer2, siret='98765432154321')
    offer1 = create_thing_offer(venue1)
    offer2 = create_thing_offer(venue2)
    paying_stock1 = create_stock_from_offer(offer1)
    paying_stock2 = create_stock_from_offer(offer2)
    free_stock1 = create_stock_from_offer(offer1, price=0)
    user = create_user()
    deposit = create_deposit(user, datetime.utcnow(), amount=500)
    booking1 = create_booking(user, paying_stock1, venue1, is_used=True)
    booking2 = create_booking(user, paying_stock1, venue1, is_used=True)
    booking3 = create_booking(user, paying_stock2, venue2, is_used=True)
    booking4 = create_booking(user, free_stock1, venue1, is_used=True)
    PcObject.check_and_save(deposit, booking1, booking2, booking3, booking4, bank_information)

    # When
    pending, not_processable = generate_new_payments()

    # Then
    assert len(pending) == 2
    assert len(not_processable) == 1


@pytest.mark.standalone
@mocked_mail
@clean_database
def test_send_transactions_should_not_send_an_email_if_pass_culture_iban_is_missing(app):
    # given
    offerer1 = create_offerer(name='first offerer')
    user = create_user()
    venue1 = create_venue(offerer1, idx=4)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    payments = [
        create_payment(booking1, offerer1, Decimal(10)),
        create_payment(booking2, offerer1, Decimal(20)),
        create_payment(booking3, offerer1, Decimal(20))
    ]

    # when
    send_transactions(payments, None, 'AZERTY9Q666', '0000', ['comptable@test.com'])

    # then
    app.mailjet_client.send.create.assert_not_called()


@pytest.mark.standalone
@mocked_mail
@clean_database
def test_send_transactions_should_not_send_an_email_if_pass_culture_bic_is_missing(app):
    # given
    offerer1 = create_offerer(name='first offerer')
    user = create_user()
    venue1 = create_venue(offerer1, idx=4)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    payments = [
        create_payment(booking1, offerer1, Decimal(10)),
        create_payment(booking2, offerer1, Decimal(20)),
        create_payment(booking3, offerer1, Decimal(20))
    ]

    # when
    send_transactions(payments, 'BD12AZERTY123456', None, '0000', ['comptable@test.com'])

    # then
    app.mailjet_client.send.create.assert_not_called()


@pytest.mark.standalone
@mocked_mail
@clean_database
def test_send_transactions_should_not_send_an_email_if_pass_culture_id_is_missing(app):
    # given
    offerer1 = create_offerer(name='first offerer')
    user = create_user()
    venue1 = create_venue(offerer1, idx=4)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    payments = [
        create_payment(booking1, offerer1, Decimal(10)),
        create_payment(booking2, offerer1, Decimal(20)),
        create_payment(booking3, offerer1, Decimal(20))
    ]

    # when
    send_transactions(payments, 'BD12AZERTY123456', 'AZERTY9Q666', None, ['comptable@test.com'])

    # then
    app.mailjet_client.send.create.assert_not_called()


@pytest.mark.standalone
@mocked_mail
@clean_database
def test_send_transactions_should_send_an_email_with_xml_attachment(app):
    # given
    offerer1 = create_offerer(name='first offerer')
    user = create_user()
    venue1 = create_venue(offerer1, idx=4)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    deposit = create_deposit(user, datetime.utcnow(), amount=500)
    PcObject.check_and_save(deposit)
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


@pytest.mark.standalone
@clean_database
@mocked_mail
@freeze_time('2018-10-15 09:21:34')
def test_send_transactions_creates_a_new_payment_transaction_if_email_was_sent_properly(app):
    # given
    offerer1 = create_offerer(name='first offerer')
    user = create_user()
    venue1 = create_venue(offerer1, idx=4)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    deposit = create_deposit(user, datetime.utcnow(), amount=500)
    payments = [
        create_payment(booking1, offerer1, Decimal(10), iban='CF13QSDFGH456789', bic='QSDFGH8Z555'),
        create_payment(booking2, offerer1, Decimal(20), iban='CF13QSDFGH456789', bic='QSDFGH8Z555'),
        create_payment(booking3, offerer1, Decimal(20), iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
    ]

    PcObject.check_and_save(deposit)
    PcObject.check_and_save(*payments)

    app.mailjet_client.send.create.return_value = Mock(status_code=200)

    # when
    send_transactions(payments, 'BD12AZERTY123456', 'AZERTY9Q666', '0000', ['comptable@test.com'])

    # then
    updated_payments = Payment.query.all()
    assert all(p.transactionMessageId == 'passCulture-SCT-20181015-092134' for p in updated_payments)
    assert all(p.transactionChecksum == payments[0].transactionChecksum for p in updated_payments)


@pytest.mark.standalone
@clean_database
@mocked_mail
@freeze_time('2018-10-15 09:21:34')
def test_send_transactions_set_status_to_sent_if_email_was_sent_properly(app):
    # given
    offerer1 = create_offerer(name='first offerer')
    user = create_user()
    venue1 = create_venue(offerer1)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    deposit = create_deposit(user, datetime.utcnow(), amount=500)
    payments = [
        create_payment(booking1, offerer1, Decimal(10), iban='CF13QSDFGH456789', bic='QSDFGH8Z555'),
        create_payment(booking2, offerer1, Decimal(20), iban='CF13QSDFGH456789', bic='QSDFGH8Z555'),
        create_payment(booking3, offerer1, Decimal(20), iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
    ]

    PcObject.check_and_save(deposit)
    PcObject.check_and_save(*payments)

    app.mailjet_client.send.create.return_value = Mock(status_code=200)

    # when
    send_transactions(payments, 'BD12AZERTY123456', 'AZERTY9Q666', '0000', ['comptable@test.com'])

    # then
    updated_payments = Payment.query.all()
    for payment in updated_payments:
        assert len(payment.statuses) == 2
        assert payment.currentStatus.status == TransactionStatus.SENT


@pytest.mark.standalone
@clean_database
@mocked_mail
@freeze_time('2018-10-15 09:21:34')
def test_send_transactions_set_status_to_error_with_details_if_email_was_not_sent_properly(
        app):
    # given
    offerer1 = create_offerer(name='first offerer')
    user = create_user()
    venue1 = create_venue(offerer1, idx=4)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    deposit = create_deposit(user, datetime.utcnow(), amount=500)
    payments = [
        create_payment(booking1, offerer1, Decimal(10), iban='CF13QSDFGH456789', bic='QSDFGH8Z555'),
        create_payment(booking2, offerer1, Decimal(20), iban='CF13QSDFGH456789', bic='QSDFGH8Z555'),
        create_payment(booking3, offerer1, Decimal(20), iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
    ]

    PcObject.check_and_save(deposit)
    PcObject.check_and_save(*payments)

    app.mailjet_client.send.create.return_value = Mock(status_code=400)

    # when
    send_transactions(payments, 'BD12AZERTY123456', 'AZERTY9Q666', '0000', ['comptable@test.com'])

    # then
    updated_payments = Payment.query.all()
    for payment in updated_payments:
        assert len(payment.statuses) == 2
        assert payment.currentStatus.status == TransactionStatus.ERROR
        assert payment.currentStatus.detail == "Erreur d'envoi à MailJet"


@pytest.mark.standalone
@clean_database
@mocked_mail
@freeze_time('2018-10-15 09:21:34')
def test_send_payment_details_sends_a_csv_attachment(app):
    # given
    offerer1 = create_offerer(name='first offerer')
    user = create_user()
    venue1 = create_venue(offerer1, idx=4)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    deposit = create_deposit(user, datetime.utcnow(), amount=500)
    payments = [
        create_payment(booking1, offerer1, Decimal(10), iban='CF13QSDFGH456789', bic='QSDFGH8Z555'),
        create_payment(booking2, offerer1, Decimal(20), iban='CF13QSDFGH456789', bic='QSDFGH8Z555'),
        create_payment(booking3, offerer1, Decimal(20), iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
    ]

    PcObject.check_and_save(deposit)
    PcObject.check_and_save(*payments)

    app.mailjet_client.send.create.return_value = Mock(status_code=200)

    # when
    send_payments_details(payments, ['comptable@test.com'])

    # then
    app.mailjet_client.send.create.assert_called_once()
    args = app.mailjet_client.send.create.call_args
    assert len(args[1]['data']['Attachments']) == 1
    assert args[1]['data']['Attachments'][0]['ContentType'] == 'text/csv'


@pytest.mark.standalone
@mocked_mail
def test_send_payment_details_does_not_send_anything_if_all_payment_have_error_status(app):
    # given
    offerer1 = create_offerer(name='first offerer')
    user = create_user()
    venue1 = create_venue(offerer1)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)

    payments = [
        create_payment(booking1, offerer1, Decimal(10), status=TransactionStatus.ERROR, iban='CF13QSDFGH456789', bic='QSDFGH8Z555'),
        create_payment(booking2, offerer1, Decimal(20), status=TransactionStatus.ERROR, iban='CF13QSDFGH456789', bic='QSDFGH8Z555'),
        create_payment(booking3, offerer1, Decimal(20), status=TransactionStatus.ERROR, iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
    ]

    # when
    send_payments_details(payments, ['comptable@test.com'])

    # then
    app.mailjet_client.send.create.assert_not_called()


@pytest.mark.standalone
@mocked_mail
def test_send_payment_details_does_not_send_anything_if_recipients_are_missing(app):
    # given
    payments = []

    # when
    send_payments_details(payments, None)

    # then
    app.mailjet_client.send.create.assert_not_called()


@pytest.mark.standalone
@clean_database
@mocked_mail
@freeze_time('2018-10-15 09:21:34')
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


@pytest.mark.standalone
@mocked_mail
def test_send_wallet_balances_does_not_send_anything_if_recipients_are_missing(app):
    # when
    send_wallet_balances(None)

    # then
    app.mailjet_client.send.create.assert_not_called()


@pytest.mark.standalone
@mocked_mail
@clean_database
def test_send_payments_report_sends_two_csv_attachments_if_some_payments_are_not_processable_and_in_error(app):
    # given
    offerer1 = create_offerer(name='first offerer')
    user = create_user()
    venue1 = create_venue(offerer1)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    deposit = create_deposit(user, datetime.utcnow(), amount=500)
    payments = [
        create_payment(booking1, offerer1, Decimal(10), status=TransactionStatus.SENT, iban='CF13QSDFGH456789', bic='QSDFGH8Z555'),
        create_payment(booking2, offerer1, Decimal(20), status=TransactionStatus.ERROR, iban='CF13QSDFGH456789', bic='QSDFGH8Z555'),
        create_payment(booking3, offerer1, Decimal(20), status=TransactionStatus.NOT_PROCESSABLE, iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
    ]

    PcObject.check_and_save(deposit)
    PcObject.check_and_save(*payments)

    app.mailjet_client.send.create.return_value = Mock(status_code=200)

    # when
    send_payments_report(payments, ['dev.team@test.com'])

    # then
    app.mailjet_client.send.create.assert_called_once()
    args = app.mailjet_client.send.create.call_args
    assert len(args[1]['data']['Attachments']) == 2
    assert args[1]['data']['Attachments'][0]['ContentType'] == 'text/csv'
    assert args[1]['data']['Attachments'][1]['ContentType'] == 'text/csv'


@pytest.mark.standalone
@mocked_mail
@clean_database
def test_send_payments_report_sends_two_csv_attachments_if_no_payments_are_in_error_or_sent(app):
    # given
    offerer1 = create_offerer(name='first offerer')
    user = create_user()
    venue1 = create_venue(offerer1)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    deposit = create_deposit(user, datetime.utcnow(), amount=500)
    payments = [
        create_payment(booking1, offerer1, Decimal(10), status=TransactionStatus.SENT, iban='CF13QSDFGH456789', bic='QSDFGH8Z555'),
        create_payment(booking2, offerer1, Decimal(20), status=TransactionStatus.SENT, iban='CF13QSDFGH456789', bic='QSDFGH8Z555'),
        create_payment(booking3, offerer1, Decimal(20), status=TransactionStatus.SENT, iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
    ]

    PcObject.check_and_save(deposit)
    PcObject.check_and_save(*payments)

    app.mailjet_client.send.create.return_value = Mock(status_code=200)

    # when
    send_payments_report(payments, ['dev.team@test.com'])

    # then
    app.mailjet_client.send.create.assert_called_once()
    args = app.mailjet_client.send.create.call_args
    assert len(args[1]['data']['Attachments']) == 2
    assert args[1]['data']['Attachments'][0]['ContentType'] == 'text/csv'
    assert args[1]['data']['Attachments'][1]['ContentType'] == 'text/csv'


@pytest.mark.standalone
@mocked_mail
@clean_database
def test_send_payments_report_does_not_send_anything_if_no_payments_are_provided(app):
    # given
    payments = []

    # when
    send_payments_report(payments, ['dev.team@test.com'])

    # then
    app.mailjet_client.send.create.assert_not_called()
