from lxml.etree import DocumentInvalid
import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.mails.testing as mails_testing
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
from pcapi.models.payment_status import PaymentStatus
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository import repository
from pcapi.scripts.payment.batch_steps import concatenate_payments_with_errors_and_retries
from pcapi.scripts.payment.batch_steps import send_payments_details
from pcapi.scripts.payment.batch_steps import send_payments_report
from pcapi.scripts.payment.batch_steps import send_transactions
from pcapi.scripts.payment.batch_steps import send_wallet_balances
from pcapi.scripts.payment.batch_steps import set_not_processable_payments_with_bank_information_to_retry


class ConcatenatePaymentsWithErrorsAndRetriesTest:
    @pytest.mark.usefixtures("db_session")
    def test_a_list_of_payments_is_returned_with_statuses_in_error_or_retry_or_pending(self):
        # Given
        booking = bookings_factories.BookingFactory()
        offerer = booking.stock.offer.venue.managingOfferer

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

        repository.save(error_payment, retry_payment, pending_payment)

        # When
        payments = concatenate_payments_with_errors_and_retries([pending_payment])

        # Then
        assert len(payments) == 3
        allowed_statuses = (TransactionStatus.RETRY, TransactionStatus.ERROR, TransactionStatus.PENDING)
        assert all(map(lambda p: p.currentStatus.status in allowed_statuses, payments))


@pytest.mark.usefixtures("db_session")
def test_send_transactions_should_not_send_an_email_if_pass_culture_iban_is_missing(app):
    # given
    iban = "CF13QSDFGH456789"
    bic = "AZERTY9Q666"
    payment1 = payments_factories.PaymentFactory(iban=iban, bic=bic)
    payment2 = payments_factories.PaymentFactory(iban=iban, bic=bic)
    payment3 = payments_factories.PaymentFactory(iban=iban, bic=bic)
    payments = [payment1, payment2, payment3]

    # when
    with pytest.raises(Exception):
        send_transactions(payments, None, bic, "0000", ["comptable@test.com"])

    # then
    assert not mails_testing.outbox


@pytest.mark.usefixtures("db_session")
def test_send_transactions_should_not_send_an_email_if_pass_culture_bic_is_missing(app):
    # given
    iban = "CF13QSDFGH456789"
    bic = "AZERTY9Q666"
    payment1 = payments_factories.PaymentFactory(iban=iban, bic=bic)
    payment2 = payments_factories.PaymentFactory(iban=iban, bic=bic)
    payment3 = payments_factories.PaymentFactory(iban=iban, bic=bic)
    payments = [payment1, payment2, payment3]

    # when
    with pytest.raises(Exception):
        send_transactions(payments, iban, None, "0000", ["comptable@test.com"])

    # then
    assert not mails_testing.outbox


@pytest.mark.usefixtures("db_session")
def test_send_transactions_should_not_send_an_email_if_pass_culture_id_is_missing(app):
    # given
    iban = "CF13QSDFGH456789"
    bic = "AZERTY9Q666"
    payment1 = payments_factories.PaymentFactory(iban=iban, bic=bic)
    payment2 = payments_factories.PaymentFactory(iban=iban, bic=bic)
    payment3 = payments_factories.PaymentFactory(iban=iban, bic=bic)
    payments = [payment1, payment2, payment3]

    # when
    with pytest.raises(Exception):
        send_transactions(payments, iban, bic, None, ["comptable@test.com"])

    # then
    assert not mails_testing.outbox


@pytest.mark.usefixtures("db_session")
def test_send_transactions_should_send_an_email_with_xml_attachment(app):
    # given
    iban = "CF13QSDFGH456789"
    bic = "AZERTY9Q666"
    payment1 = payments_factories.PaymentFactory(iban=iban, bic=bic)
    payment2 = payments_factories.PaymentFactory(iban=iban, bic=bic)
    payment3 = payments_factories.PaymentFactory(iban=iban, bic=bic)
    payments = [payment1, payment2, payment3]

    # when
    send_transactions(payments, iban, bic, "0000", ["comptable@test.com"])

    # then
    assert len(mails_testing.outbox) == 1
    assert len(mails_testing.outbox[0].sent_data["Attachments"]) == 1


@pytest.mark.usefixtures("db_session")
def test_send_transactions_creates_a_new_payment_transaction_if_email_was_sent_properly(app):
    # given
    iban = "CF13QSDFGH456789"
    bic = "AZERTY9Q666"
    payment1 = payments_factories.PaymentFactory(iban=iban, bic=bic)
    payment2 = payments_factories.PaymentFactory(iban=iban, bic=bic)
    payment3 = payments_factories.PaymentFactory(iban=iban, bic=bic)
    payments = [payment1, payment2, payment3]

    # when
    send_transactions(payments, "BD12AZERTY123456", "AZERTY9Q666", "0000", ["comptable@test.com"])

    # then
    payment_messages = {p.paymentMessage for p in Payment.query.all()}
    assert len(payment_messages) == 1
    assert payment_messages != {None}


@pytest.mark.usefixtures("db_session")
def test_send_transactions_set_status_to_sent_if_email_was_sent_properly(app):
    # given
    iban = "CF13QSDFGH456789"
    bic = "AZERTY9Q666"
    payment1 = payments_factories.PaymentFactory(iban=iban, bic=bic)
    payment2 = payments_factories.PaymentFactory(iban=iban, bic=bic)
    payment3 = payments_factories.PaymentFactory(iban=iban, bic=bic)
    payments = [payment1, payment2, payment3]

    # when
    send_transactions(payments, iban, bic, "0000", ["comptable@test.com"])

    # then
    updated_payments = Payment.query.all()
    for payment in updated_payments:
        assert len(payment.statuses) == 2
        assert payment.currentStatus.status == TransactionStatus.UNDER_REVIEW


@pytest.mark.usefixtures("db_session")
@override_settings(EMAIL_BACKEND="pcapi.core.mails.backends.testing.FailingBackend")
def test_send_transactions_set_status_to_error_with_details_if_email_was_not_sent_properly(app):
    # given
    iban = "CF13QSDFGH456789"
    bic = "AZERTY9Q666"
    payment1 = payments_factories.PaymentFactory(iban=iban, bic=bic)
    payment2 = payments_factories.PaymentFactory(iban=iban, bic=bic)
    payments = [payment1, payment2]

    # when
    send_transactions(payments, iban, bic, "0000", ["comptable@test.com"])

    # then
    updated_payments = Payment.query.all()
    for payment in updated_payments:
        assert len(payment.statuses) == 2
        assert payment.currentStatus.status == TransactionStatus.ERROR
        assert payment.currentStatus.detail == "Erreur d'envoi à MailJet"


@pytest.mark.usefixtures("db_session")
def test_send_transactions_with_malformed_iban_on_payments_gives_them_an_error_status_with_a_cause(app):
    # given
    payment = payments_factories.PaymentFactory(iban="CF  13QSDFGH45 qbc //")

    # when
    with pytest.raises(DocumentInvalid):
        send_transactions([payment], "BD12AZERTY123456", payment.bic, "0000", ["comptable@test.com"])

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
def test_send_payment_details_sends_a_csv_attachment(app):
    # given
    iban = "CF13QSDFGH456789"
    bic = "AZERTY9Q666"
    payment = payments_factories.PaymentFactory(iban=iban, bic=bic)

    # when
    send_payments_details([payment], ["comptable@test.com"])

    # then
    assert len(mails_testing.outbox) == 1
    assert len(mails_testing.outbox[0].sent_data["Attachments"]) == 1
    assert mails_testing.outbox[0].sent_data["Attachments"][0]["ContentType"] == "application/zip"


@pytest.mark.usefixtures("db_session")
def test_send_payment_details_does_not_send_anything_if_all_payment_have_error_status(app):
    # given
    iban = "CF13QSDFGH456789"
    bic = "AZERTY9Q666"
    payment = payments_factories.PaymentFactory(iban=iban, bic=bic, statuses=[])
    payments_factories.PaymentStatusFactory(payment=payment, status=TransactionStatus.ERROR)

    # when
    send_payments_details([payment], ["comptable@test.com"])

    # then
    assert not mails_testing.outbox


def test_send_payment_details_does_not_send_anything_if_recipients_are_missing(app):
    # given
    payments = []

    # when
    with pytest.raises(Exception):
        send_payments_details(payments, None)

    # then
    assert not mails_testing.outbox


@pytest.mark.usefixtures("db_session")
def test_send_wallet_balances_sends_a_csv_attachment(app):
    # when
    send_wallet_balances(["comptable@test.com"])

    # then
    assert len(mails_testing.outbox) == 1
    assert len(mails_testing.outbox[0].sent_data["Attachments"]) == 1
    assert mails_testing.outbox[0].sent_data["Attachments"][0]["ContentType"] == "text/csv"


def test_send_wallet_balances_does_not_send_anything_if_recipients_are_missing(app):
    # when
    with pytest.raises(Exception):
        send_wallet_balances(None)

    # then
    assert not mails_testing.outbox


@pytest.mark.usefixtures("db_session")
def test_send_payments_report_sends_two_csv_attachments_if_some_payments_are_not_processable_and_in_error(app):
    # given
    iban = "CF13QSDFGH456789"
    bic = "QSDFGH8Z555"
    payment1 = payments_factories.PaymentFactory(iban=iban, bic=bic, statuses=[])
    payments_factories.PaymentStatusFactory(payment=payment1, status=TransactionStatus.SENT)
    payment2 = payments_factories.PaymentFactory(iban=iban, bic=bic, statuses=[])
    payments_factories.PaymentStatusFactory(payment=payment2, status=TransactionStatus.ERROR)
    payment3 = payments_factories.PaymentFactory(iban=iban, bic=bic, statuses=[])
    payments_factories.PaymentStatusFactory(payment=payment3, status=TransactionStatus.NOT_PROCESSABLE)
    payments = [payment1, payment2, payment3]

    # when
    send_payments_report(payments, ["dev.team@test.com"])

    # then
    assert len(mails_testing.outbox) == 1
    assert len(mails_testing.outbox[0].sent_data["Attachments"]) == 2
    assert mails_testing.outbox[0].sent_data["Attachments"][0]["ContentType"] == "text/csv"
    assert mails_testing.outbox[0].sent_data["Attachments"][1]["ContentType"] == "text/csv"


@pytest.mark.usefixtures("db_session")
def test_send_payments_report_sends_two_csv_attachments_if_no_payments_are_in_error_or_sent(app):
    # given
    iban = "CF13QSDFGH456789"
    bic = "QSDFGH8Z555"
    payment1 = payments_factories.PaymentFactory(iban=iban, bic=bic, statuses=[])
    payment2 = payments_factories.PaymentFactory(iban=iban, bic=bic, statuses=[])
    for payment in (payment1, payment2):
        payments_factories.PaymentStatusFactory(payment=payment, status=TransactionStatus.SENT)
    payments = [payment1, payment2]

    # when
    send_payments_report(payments, ["dev.team@test.com"])

    # then
    assert len(mails_testing.outbox) == 1
    assert len(mails_testing.outbox[0].sent_data["Attachments"]) == 2
    assert mails_testing.outbox[0].sent_data["Attachments"][0]["ContentType"] == "text/csv"
    assert mails_testing.outbox[0].sent_data["Attachments"][1]["ContentType"] == "text/csv"


@pytest.mark.usefixtures("db_session")
def test_send_payments_report_does_not_send_anything_if_no_payments_are_provided(app):
    # given
    payments = []

    # when
    send_payments_report(payments, ["dev.team@test.com"])

    # then
    assert not mails_testing.outbox


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

        # When
        set_not_processable_payments_with_bank_information_to_retry()

        # Then
        queried_not_processable_payment = Payment.query.filter_by(id=not_processable_payment.id).one()
        queried_sent_payment = Payment.query.filter_by(id=sent_payment.id).one()
        assert queried_not_processable_payment.iban == "FR7611808009101234567890147"
        assert queried_not_processable_payment.bic == "CCBPFRPPVER"
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

        # When
        set_not_processable_payments_with_bank_information_to_retry()

        # Then
        queried_not_processable_payment = Payment.query.filter_by(id=not_processable_payment.id).one()
        queried_sent_payment = Payment.query.filter_by(id=sent_payment.id).one()
        assert queried_not_processable_payment.iban == None
        assert queried_not_processable_payment.bic == None
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

        # When
        set_not_processable_payments_with_bank_information_to_retry()

        # Then
        queried_not_processable_payment = Payment.query.filter_by(id=not_processable_payment.id).one()
        assert queried_not_processable_payment.iban == "FR7611808009101234567890147"
        assert queried_not_processable_payment.bic == "CCBPFRPPVER"
