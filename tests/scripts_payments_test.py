from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock
from uuid import UUID

import pytest
from freezegun import freeze_time

from models import PcObject
from models.payment import Payment
from models.payment_status import TransactionStatus
from scripts.payments import do_generate_payments, do_send_payments
from tests.conftest import clean_database, mocked_mail
from utils.test_utils import create_offerer, create_venue, create_thing_offer, create_stock_from_offer, \
    create_booking, create_user, create_deposit, create_payment


@pytest.mark.standalone
@clean_database
def test_do_generate_payments_records_new_payment_lines_in_database(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_thing_offer(venue)
    stock = create_stock_from_offer(offer)
    user = create_user()
    deposit = create_deposit(user, datetime.utcnow(), amount=500)
    booking1 = create_booking(user, stock, venue, is_used=True)
    booking2 = create_booking(user, stock, venue, is_used=True)
    booking3 = create_booking(user, stock, venue, is_used=True)
    payment1 = create_payment(booking2, offerer, 10)

    PcObject.check_and_save(deposit, booking1, booking3, payment1)

    initial_payment_count = Payment.query.count()

    # When
    do_generate_payments()

    # Then
    assert Payment.query.count() - initial_payment_count == 2


@pytest.mark.standalone
@mocked_mail
@clean_database
def test_do_send_payments_should_not_send_an_email_if_pass_culture_iban_is_missing(app):
    # given
    offerer1 = create_offerer(name='first offerer', iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    user = create_user()
    venue1 = create_venue(offerer1, idx=4)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    payments = [
        create_payment(booking1, offerer1, Decimal(10), idx=7),
        create_payment(booking2, offerer1, Decimal(20), idx=8),
        create_payment(booking3, offerer1, Decimal(20), idx=9)
    ]

    # when
    do_send_payments(payments, None, 'AZERTY9Q666', '0000')

    # then
    app.mailjet_client.send.create.assert_not_called()


@pytest.mark.standalone
@mocked_mail
@clean_database
def test_do_send_payments_should_not_send_an_email_if_pass_culture_bic_is_missing(app):
    # given
    offerer1 = create_offerer(name='first offerer', iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    user = create_user()
    venue1 = create_venue(offerer1, idx=4)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    payments = [
        create_payment(booking1, offerer1, Decimal(10), idx=7),
        create_payment(booking2, offerer1, Decimal(20), idx=8),
        create_payment(booking3, offerer1, Decimal(20), idx=9)
    ]

    # when
    do_send_payments(payments, 'BD12AZERTY123456', None, '0000')

    # then
    app.mailjet_client.send.create.assert_not_called()


@pytest.mark.standalone
@mocked_mail
@clean_database
def test_do_send_payments_should_not_send_an_email_if_pass_culture_id_is_missing(app):
    # given
    offerer1 = create_offerer(name='first offerer', iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    user = create_user()
    venue1 = create_venue(offerer1, idx=4)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    payments = [
        create_payment(booking1, offerer1, Decimal(10), idx=7),
        create_payment(booking2, offerer1, Decimal(20), idx=8),
        create_payment(booking3, offerer1, Decimal(20), idx=9)
    ]

    # when
    do_send_payments(payments, 'BD12AZERTY123456', 'AZERTY9Q666', None)

    # then
    app.mailjet_client.send.create.assert_not_called()


@pytest.mark.standalone
@mocked_mail
@clean_database
def test_do_send_payments_should_send_an_email_with_xml_attachment(app):
    # given
    offerer1 = create_offerer(name='first offerer', iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    user = create_user()
    venue1 = create_venue(offerer1, idx=4)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    deposit = create_deposit(user, datetime.utcnow(), amount=500)
    PcObject.check_and_save(deposit)
    payments = [
        create_payment(booking1, offerer1, Decimal(10), idx=7),
        create_payment(booking2, offerer1, Decimal(20), idx=8),
        create_payment(booking3, offerer1, Decimal(20), idx=9)
    ]

    app.mailjet_client.send.create.return_value = Mock(status_code=200)

    # when
    do_send_payments(payments, 'BD12AZERTY123456', 'AZERTY9Q666', '0000')

    # then
    app.mailjet_client.send.create.assert_called_once()
    args = app.mailjet_client.send.create.call_args
    assert len(args[1]['data']['Attachments']) == 1


@pytest.mark.standalone
@clean_database
@mocked_mail
@freeze_time('2018-10-15 09:21:34')
def test_do_send_payments_updates_payments_with_message_id_and_end_to_end_id_and_status_if_email_sent(app):
    # given
    offerer1 = create_offerer(name='first offerer', iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    user = create_user()
    venue1 = create_venue(offerer1, idx=4)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    deposit = create_deposit(user, datetime.utcnow(), amount=500)
    payments = [
        create_payment(booking1, offerer1, Decimal(10), idx=7),
        create_payment(booking2, offerer1, Decimal(20), idx=8),
        create_payment(booking3, offerer1, Decimal(20), idx=9)
    ]

    PcObject.check_and_save(deposit)
    PcObject.check_and_save(*payments)

    app.mailjet_client.send.create.return_value = Mock(status_code=200)

    # when
    do_send_payments(payments, 'BD12AZERTY123456', 'AZERTY9Q666', '0000')

    # then
    updated_payments = Payment.query.all()
    for payment in updated_payments:
        assert payment.transactionMessageId == 'passCulture-SCT-20181015-092134'
        assert payment.transactionEndToEndId is not None
        assert type(payment.transactionEndToEndId) is UUID
        assert len(payment.statuses) == 2
        assert payment.statuses[1].status == TransactionStatus.SENT


@pytest.mark.standalone
@clean_database
@mocked_mail
@freeze_time('2018-10-15 09:21:34')
def test_do_send_payments_does_not_update_payments_with_message_id_and_end_to_end_id_and_status_if_email_was_not_sent_properly(
        app):
    # given
    offerer1 = create_offerer(name='first offerer', iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    user = create_user()
    venue1 = create_venue(offerer1, idx=4)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock1)
    booking3 = create_booking(user, stock1)
    deposit = create_deposit(user, datetime.utcnow(), amount=500)
    payments = [
        create_payment(booking1, offerer1, Decimal(10), idx=7),
        create_payment(booking2, offerer1, Decimal(20), idx=8),
        create_payment(booking3, offerer1, Decimal(20), idx=9)
    ]

    PcObject.check_and_save(deposit)
    PcObject.check_and_save(*payments)

    app.mailjet_client.send.create.return_value = Mock(status_code=400)

    # when
    do_send_payments(payments, 'BD12AZERTY123456', 'AZERTY9Q666', '0000')

    # then
    updated_payments = Payment.query.all()
    for payment in updated_payments:
        assert payment.transactionMessageId is None
        assert payment.transactionEndToEndId is None
        assert len(payment.statuses) == 1
        assert payment.statuses[0].status == TransactionStatus.PENDING
