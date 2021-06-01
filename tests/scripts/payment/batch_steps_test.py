import datetime

from lxml.etree import DocumentInvalid
import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.mails.testing as mails_testing
import pcapi.core.offers.factories as offers_factories
import pcapi.core.payments.factories as payments_factories
from pcapi.core.testing import override_settings
from pcapi.model_creators.generic_creators import create_bank_information
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_payment
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_stock_from_offer
from pcapi.models.bank_information import BankInformationStatus
from pcapi.models.payment import Payment
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository import repository
from pcapi.scripts.payment.batch_steps import get_venues_to_reimburse
from pcapi.scripts.payment.batch_steps import send_payments_details
from pcapi.scripts.payment.batch_steps import send_payments_report
from pcapi.scripts.payment.batch_steps import send_transactions
from pcapi.scripts.payment.batch_steps import send_wallet_balances
from pcapi.scripts.payment.batch_steps import set_not_processable_payments_with_bank_information_to_retry


@pytest.mark.usefixtures("db_session")
def test_send_transactions_should_not_send_an_email_if_pass_culture_iban_is_missing():
    # given
    iban = "CF13QSDFGH456789"
    bic = "AZERTY9Q666"
    payments_factories.PaymentFactory(iban=iban, bic=bic)
    payments_factories.PaymentFactory(iban=iban, bic=bic)
    payments_factories.PaymentFactory(iban=iban, bic=bic)

    # when
    with pytest.raises(Exception):
        send_transactions(Payment.query, None, bic, "0000", ["comptable@test.com"])

    # then
    assert not mails_testing.outbox


@pytest.mark.usefixtures("db_session")
def test_send_transactions_should_not_send_an_email_if_pass_culture_bic_is_missing():
    # given
    iban = "CF13QSDFGH456789"
    bic = "AZERTY9Q666"
    payments_factories.PaymentFactory(iban=iban, bic=bic)
    payments_factories.PaymentFactory(iban=iban, bic=bic)
    payments_factories.PaymentFactory(iban=iban, bic=bic)

    # when
    with pytest.raises(Exception):
        send_transactions(Payment.query, iban, None, "0000", ["comptable@test.com"])

    # then
    assert not mails_testing.outbox


@pytest.mark.usefixtures("db_session")
def test_send_transactions_should_not_send_an_email_if_pass_culture_id_is_missing():
    # given
    iban = "CF13QSDFGH456789"
    bic = "AZERTY9Q666"
    payments_factories.PaymentFactory(iban=iban, bic=bic)
    payments_factories.PaymentFactory(iban=iban, bic=bic)
    payments_factories.PaymentFactory(iban=iban, bic=bic)

    # when
    with pytest.raises(Exception):
        send_transactions(Payment.query, iban, bic, None, ["comptable@test.com"])

    # then
    assert not mails_testing.outbox


@pytest.mark.usefixtures("db_session")
def test_send_transactions_should_send_an_email_with_xml_attachment():
    # given
    iban = "CF13QSDFGH456789"
    bic = "AZERTY9Q666"
    payments_factories.PaymentFactory(iban=iban, bic=bic)
    payments_factories.PaymentFactory(iban=iban, bic=bic)
    payments_factories.PaymentFactory(iban=iban, bic=bic)

    # when
    send_transactions(Payment.query, iban, bic, "0000", ["x@example.com"])

    # then
    assert len(mails_testing.outbox) == 1
    assert len(mails_testing.outbox[0].sent_data["Attachments"]) == 1


@pytest.mark.usefixtures("db_session")
def test_send_transactions_creates_a_new_payment_transaction_if_email_was_sent_properly():
    # given
    iban = "CF13QSDFGH456789"
    bic = "AZERTY9Q666"
    payments_factories.PaymentFactory(iban=iban, bic=bic)
    payments_factories.PaymentFactory(iban=iban, bic=bic)
    payments_factories.PaymentFactory(iban=iban, bic=bic)

    # when
    send_transactions(Payment.query, "BD12AZERTY123456", "AZERTY9Q666", "0000", ["comptable@test.com"])

    # then
    payment_messages = {p.paymentMessage for p in Payment.query.all()}
    assert len(payment_messages) == 1
    assert payment_messages != {None}


@pytest.mark.usefixtures("db_session")
def test_send_transactions_set_status_to_sent_if_email_was_sent_properly():
    # given
    iban = "CF13QSDFGH456789"
    bic = "AZERTY9Q666"
    payments_factories.PaymentFactory(iban=iban, bic=bic)
    payments_factories.PaymentFactory(iban=iban, bic=bic)
    payments_factories.PaymentFactory(iban=iban, bic=bic)

    # when
    send_transactions(Payment.query, iban, bic, "0000", ["comptable@test.com"])

    # then
    payments = Payment.query.all()
    for payment in payments:
        assert len(payment.statuses) == 2
        assert payment.currentStatus.status == TransactionStatus.UNDER_REVIEW


@pytest.mark.usefixtures("db_session")
@override_settings(EMAIL_BACKEND="pcapi.core.mails.backends.testing.FailingBackend")
def test_send_transactions_set_status_to_error_with_details_if_email_was_not_sent_properly():
    # given
    iban = "CF13QSDFGH456789"
    bic = "AZERTY9Q666"
    payments_factories.PaymentFactory(iban=iban, bic=bic)
    payments_factories.PaymentFactory(iban=iban, bic=bic)

    # when
    send_transactions(Payment.query, iban, bic, "0000", ["comptable@test.com"])

    # then
    payments = Payment.query.all()
    for payment in payments:
        assert len(payment.statuses) == 2
        assert payment.currentStatus.status == TransactionStatus.ERROR
        assert payment.currentStatus.detail == "Erreur d'envoi à MailJet"


@pytest.mark.usefixtures("db_session")
def test_send_transactions_with_malformed_iban_on_payments_gives_them_an_error_status_with_a_cause():
    # given
    payments_factories.PaymentFactory(iban="CF  13QSDFGH45 qbc //")

    # when
    with pytest.raises(DocumentInvalid):
        send_transactions(Payment.query, "BD12AZERTY123456", "AZERTY9Q666", "0000", ["comptable@test.com"])

    # then
    payment = Payment.query.one()
    assert len(payment.statuses) == 2
    assert payment.currentStatus.status == TransactionStatus.NOT_PROCESSABLE
    assert (
        payment.currentStatus.detail == "Element '{urn:iso:std:iso:20022:tech:xsd:pain.001.001.03}IBAN': "
        "[facet 'pattern'] The value 'CF  13QSDFGH45 qbc //' is not accepted "
        "by the pattern '[A-Z]{2,2}[0-9]{2,2}[a-zA-Z0-9]{1,30}'., line 76"
    )


@pytest.mark.usefixtures("db_session")
def test_send_payment_details_sends_a_csv_attachment():
    # given
    iban = "CF13QSDFGH456789"
    bic = "AZERTY9Q666"
    payments_factories.PaymentFactory(iban=iban, bic=bic)

    # when
    send_payments_details(Payment.query, ["comptable@test.com"])

    # then
    assert len(mails_testing.outbox) == 1
    assert len(mails_testing.outbox[0].sent_data["Attachments"]) == 1
    assert mails_testing.outbox[0].sent_data["Attachments"][0]["ContentType"] == "application/zip"


@pytest.mark.usefixtures("db_session")
def test_send_payment_details_does_not_send_anything_if_all_payment_have_error_status():
    send_payments_details(Payment.query, ["comptable@test.com"])
    assert not mails_testing.outbox


def test_send_payment_details_does_not_send_anything_if_recipients_are_missing():
    with pytest.raises(Exception):
        send_payments_details(Payment.query, None)

    assert not mails_testing.outbox


@pytest.mark.usefixtures("db_session")
def test_send_wallet_balances_sends_a_csv_attachment():
    # when
    send_wallet_balances(["comptable@test.com"])

    # then
    assert len(mails_testing.outbox) == 1
    assert len(mails_testing.outbox[0].sent_data["Attachments"]) == 1
    assert mails_testing.outbox[0].sent_data["Attachments"][0]["ContentType"] == "text/csv"


def test_send_wallet_balances_does_not_send_anything_if_recipients_are_missing():
    # when
    with pytest.raises(Exception):
        send_wallet_balances(None)

    # then
    assert not mails_testing.outbox


@pytest.mark.usefixtures("db_session")
def test_send_payments_report_sends_two_csv_attachments_if_some_payments_are_not_processable_and_in_error():
    # given
    batch_date = datetime.datetime.now()
    payments = payments_factories.PaymentFactory.create_batch(3, statuses=[], batchDate=batch_date)
    payments_factories.PaymentStatusFactory(payment=payments[0], status=TransactionStatus.UNDER_REVIEW)
    payments_factories.PaymentStatusFactory(payment=payments[1], status=TransactionStatus.ERROR)
    payments_factories.PaymentStatusFactory(payment=payments[2], status=TransactionStatus.NOT_PROCESSABLE)

    # when
    send_payments_report(batch_date, ["recipient@example.com"])

    # then
    assert len(mails_testing.outbox) == 1
    assert len(mails_testing.outbox[0].sent_data["Attachments"]) == 2
    assert mails_testing.outbox[0].sent_data["Attachments"][0]["ContentType"] == "text/csv"
    assert mails_testing.outbox[0].sent_data["Attachments"][1]["ContentType"] == "text/csv"


class SetNotProcessablePaymentsWithBankInformationToRetryTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_set_not_processable_payments_to_retry_and_update_payments_bic_and_iban_using_offerer_information(
        self,
    ):
        # Given
        offerer = create_offerer(name="first offerer")
        user = create_user()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer, price=0)
        booking = create_booking(user=user, stock=stock)
        bank_information = create_bank_information(
            offerer=offerer, iban="FR7611808009101234567890147", bic="CCBPFRPPVER"
        )
        not_processable_payment = create_payment(
            booking, offerer, 10, status=TransactionStatus.NOT_PROCESSABLE, iban=None, bic=None
        )
        sent_payment = create_payment(booking, offerer, 10, status=TransactionStatus.SENT)
        repository.save(bank_information, not_processable_payment, sent_payment)
        new_batch_date = datetime.datetime.now()

        # When
        set_not_processable_payments_with_bank_information_to_retry(new_batch_date)

        # Then
        queried_not_processable_payment = Payment.query.filter_by(id=not_processable_payment.id).one()
        queried_sent_payment = Payment.query.filter_by(id=sent_payment.id).one()
        assert queried_not_processable_payment.iban == "FR7611808009101234567890147"
        assert queried_not_processable_payment.bic == "CCBPFRPPVER"
        assert queried_not_processable_payment.batchDate == new_batch_date
        assert queried_not_processable_payment.currentStatus.status == TransactionStatus.RETRY
        assert queried_sent_payment.currentStatus.status == TransactionStatus.SENT

    @pytest.mark.usefixtures("db_session")
    def test_should_not_set_not_processable_payments_to_retry_when_bank_information_status_is_not_accepted(self):
        # Given
        offerer = create_offerer(name="first offerer")
        user = create_user()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer, price=0)
        booking = create_booking(user=user, stock=stock)
        bank_information = create_bank_information(
            offerer=offerer, iban=None, bic=None, status=BankInformationStatus.DRAFT
        )
        not_processable_payment = create_payment(
            booking, offerer, 10, status=TransactionStatus.NOT_PROCESSABLE, iban=None, bic=None
        )
        sent_payment = create_payment(booking, offerer, 10, status=TransactionStatus.SENT)
        repository.save(bank_information, not_processable_payment, sent_payment)
        new_batch_date = datetime.datetime.now()

        # When

        set_not_processable_payments_with_bank_information_to_retry(new_batch_date)

        # Then
        queried_not_processable_payment = Payment.query.filter_by(id=not_processable_payment.id).one()
        queried_sent_payment = Payment.query.filter_by(id=sent_payment.id).one()
        assert queried_not_processable_payment.iban == None
        assert queried_not_processable_payment.bic == None
        assert queried_not_processable_payment.batchDate != new_batch_date
        assert queried_not_processable_payment.currentStatus.status == TransactionStatus.NOT_PROCESSABLE
        assert queried_sent_payment.currentStatus.status == TransactionStatus.SENT

    @pytest.mark.usefixtures("db_session")
    def test_should_set_not_processable_payments_to_retry_and_update_payments_bic_and_iban_using_venue_information(
        self,
    ):
        # Given
        offerer = create_offerer(name="first offerer")
        user = create_user()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer, price=0)
        booking = create_booking(user=user, stock=stock)
        bank_information = create_bank_information(
            venue=venue,
            iban="FR7611808009101234567890147",
            bic="CCBPFRPPVER",
        )
        not_processable_payment = create_payment(
            booking, offerer, 10, status=TransactionStatus.NOT_PROCESSABLE, iban=None, bic=None
        )
        sent_payment = create_payment(
            booking, offerer, 10, status=TransactionStatus.SENT, iban="FR7630007000111234567890144", bic="BDFEFR2LCCB"
        )
        repository.save(bank_information, not_processable_payment, sent_payment)
        new_batch_date = datetime.datetime.now()

        # When
        set_not_processable_payments_with_bank_information_to_retry(new_batch_date)

        # Then
        queried_not_processable_payment = Payment.query.filter_by(id=not_processable_payment.id).one()
        assert queried_not_processable_payment.iban == "FR7611808009101234567890147"
        assert queried_not_processable_payment.bic == "CCBPFRPPVER"
        assert queried_not_processable_payment.batchDate == new_batch_date


@pytest.mark.usefixtures("db_session")
def test_get_venues_to_reimburse():
    venue1 = offers_factories.VenueFactory(name="name")
    # Two matching bookings for this venue, but it should onmy appear once.
    bookings_factories.BookingFactory(isUsed=True, stock__offer__venue=venue1)
    bookings_factories.BookingFactory(isUsed=True, stock__offer__venue=venue1)
    venue2 = offers_factories.VenueFactory(publicName="public name")
    bookings_factories.BookingFactory(isUsed=True, stock__offer__venue=venue2)
    bookings_factories.BookingFactory(isUsed=False, stock__offer__venue__publicName="booking not used")
    payments_factories.PaymentFactory(booking__stock__offer__venue__publicName="already has a payment")

    venues = get_venues_to_reimburse()
    assert len(venues) == 2
    assert set(venues) == {(venue1.id, "name"), (venue2.id, "public name")}
