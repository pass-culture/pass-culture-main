import datetime
import uuid

import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.payments.factories as factories
import pcapi.core.users.factories as users_factories
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_payment
from pcapi.model_creators.generic_creators import create_payment_message
from pcapi.models.bank_information import BankInformationStatus
from pcapi.models.payment import Payment
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository import payment_queries
from pcapi.repository import repository


class FindPaymentsByMessageTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_payments_matching_message(self, app):
        # given
        beneficiary = users_factories.BeneficiaryFactory()
        booking = create_booking(user=beneficiary)
        offerer = booking.stock.offer.venue.managingOfferer
        transaction1 = create_payment_message(name="XML1")
        transaction2 = create_payment_message(name="XML2")
        transaction3 = create_payment_message(name="XML3")
        uuid1, uuid2, uuid3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
        payments = [
            create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid1, payment_message=transaction1),
            create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid2, payment_message=transaction2),
            create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid1, payment_message=transaction3),
            create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid3, payment_message=transaction1),
            create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid1, payment_message=transaction1),
        ]
        repository.save(*payments)

        # when
        matching_payments = payment_queries.find_payments_by_message("XML1")

        # then
        assert len(matching_payments) == 3
        for payment in matching_payments:
            assert payment.paymentMessageName == "XML1"

    @pytest.mark.usefixtures("db_session")
    def test_returns_nothing_if_message_is_not_matched(self, app):
        # given
        beneficiary = users_factories.BeneficiaryFactory()
        booking = create_booking(user=beneficiary)
        offerer = booking.stock.offer.venue.managingOfferer
        message1 = create_payment_message(name="XML1")
        message2 = create_payment_message(name="XML2")
        message3 = create_payment_message(name="XML3")
        uuid1, uuid2, uuid3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
        payments = [
            create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid1, payment_message=message1),
            create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid2, payment_message=message2),
            create_payment(booking, offerer, 5, transaction_end_to_end_id=uuid3, payment_message=message3),
        ]
        repository.save(*payments)

        # when
        matching_payments = payment_queries.find_payments_by_message("unknown message")

        # then
        assert matching_payments == []


class FindNotProcessableWithBankInformationTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_payments_to_retry_if_no_bank_information(self, app):
        # Given
        product = offers_factories.ThingProductFactory(name="Lire un livre", isNational=True)
        venue = offers_factories.VenueFactory(postalCode="34000", departementCode="34")
        offer = offers_factories.ThingOfferFactory(product=product, venue=venue)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0, quantity=2)
        booking = bookings_factories.BookingFactory(stock=stock, quantity=2, isCancelled=True)
        payment = factories.PaymentFactory(booking=booking, amount=10, iban="CF13QSDFGH456789", bic="QSDFGH8Z555")
        factories.PaymentStatusFactory(payment=payment, status=TransactionStatus.NOT_PROCESSABLE)

        # When
        payments_to_retry = payment_queries.find_not_processable_with_bank_information()

        # Then
        assert payments_to_retry == []

    @pytest.mark.usefixtures("db_session")
    def test_should_return_payment_to_retry_if_bank_information_linked_to_offerer_and_current_status_is_not_processable(
        self, app
    ):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        product = offers_factories.ThingProductFactory(name="Lire un livre", isNational=True)
        venue = offers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, postalCode="34000", departementCode="34"
        )
        offer = offers_factories.ThingOfferFactory(product=product, venue=venue)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        booking = bookings_factories.BookingFactory(stock=stock)
        not_processable_payment = factories.PaymentFactory(
            booking=booking, amount=10, iban="CF13QSDFGH456789", bic="QSDFGH8Z555"
        )
        factories.PaymentStatusFactory(payment=not_processable_payment, status=TransactionStatus.NOT_PROCESSABLE)
        offers_factories.BankInformationFactory(offerer=user_offerer.offerer)

        # When
        payments_to_retry = payment_queries.find_not_processable_with_bank_information()

        # Then
        assert not_processable_payment in payments_to_retry

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_payments_to_retry_if_bank_information_linked_to_offerer_and_current_status_is_not_not_processable(
        self, app
    ):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        product = offers_factories.ThingProductFactory(name="Lire un livre", isNational=True)
        venue = offers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, postalCode="34000", departementCode="34"
        )
        offer = offers_factories.ThingOfferFactory(product=product, venue=venue)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        booking = bookings_factories.BookingFactory(stock=stock)
        not_processable_payment = factories.PaymentFactory(
            booking=booking, amount=10, iban="CF13QSDFGH456789", bic="QSDFGH8Z555"
        )
        factories.PaymentStatusFactory(payment=not_processable_payment, status=TransactionStatus.NOT_PROCESSABLE)
        offers_factories.BankInformationFactory(offerer=user_offerer.offerer)

        # When
        not_processable_payment.setStatus(TransactionStatus.SENT)
        payments_to_retry = payment_queries.find_not_processable_with_bank_information()

        # Then
        assert payments_to_retry == []

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_payment_to_retry_if_bank_information_status_is_not_accepted(self, app):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        product = offers_factories.ThingProductFactory(name="Lire un livre", isNational=True)
        venue = offers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, postalCode="34000", departementCode="34"
        )
        offer = offers_factories.ThingOfferFactory(product=product, venue=venue)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        booking = bookings_factories.BookingFactory(stock=stock)
        not_processable_payment = factories.PaymentFactory(
            booking=booking, amount=10, iban="CF13QSDFGH456789", bic="QSDFGH8Z555"
        )
        factories.PaymentStatusFactory(payment=not_processable_payment, status=TransactionStatus.NOT_PROCESSABLE)
        offers_factories.BankInformationFactory(
            offerer=user_offerer.offerer, iban=None, bic=None, status=BankInformationStatus.DRAFT
        )

        # When
        payments_to_retry = payment_queries.find_not_processable_with_bank_information()

        # Then
        assert payments_to_retry == []

    @pytest.mark.usefixtures("db_session")
    def test_should_return_payment_to_retry_if_bank_information_linked_to_venue_and_current_status_is_not_processable(
        self, app
    ):
        # Given
        user_offerer = offers_factories.UserOffererFactory()
        product = offers_factories.ThingProductFactory(name="Lire un livre", isNational=True)
        venue = offers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, postalCode="34000", departementCode="34"
        )
        offer = offers_factories.ThingOfferFactory(product=product, venue=venue)
        stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        booking = bookings_factories.BookingFactory(stock=stock)
        not_processable_payment = factories.PaymentFactory(
            booking=booking, amount=10, iban="CF13QSDFGH456789", bic="QSDFGH8Z555"
        )
        factories.PaymentStatusFactory(payment=not_processable_payment, status=TransactionStatus.NOT_PROCESSABLE)
        offers_factories.BankInformationFactory(offerer=user_offerer.offerer)

        # When
        payments_to_retry = payment_queries.find_not_processable_with_bank_information()

        # Then
        assert not_processable_payment in payments_to_retry


@pytest.mark.usefixtures("db_session")
def test_has_payment():
    booking = bookings_factories.BookingFactory()
    assert not payment_queries.has_payment(booking)

    factories.PaymentFactory(booking=booking)
    assert payment_queries.has_payment(booking)


@pytest.mark.usefixtures("db_session")
def test_get_payment_count_by_status():
    batch_date = datetime.datetime.now()
    other_date = datetime.datetime.now()

    count = payment_queries.get_payment_count_by_status(batch_date)
    assert count == {}

    factories.PaymentStatusFactory(status=TransactionStatus.NOT_PROCESSABLE, payment__batchDate=other_date)
    count = payment_queries.get_payment_count_by_status(batch_date)
    assert count == {}

    ps = factories.PaymentStatusFactory(status=TransactionStatus.NOT_PROCESSABLE, payment__batchDate=batch_date)
    count = payment_queries.get_payment_count_by_status(batch_date)
    assert count == {"NOT_PROCESSABLE": 1}

    factories.PaymentStatusFactory(status=TransactionStatus.NOT_PROCESSABLE, payment__batchDate=batch_date)
    count = payment_queries.get_payment_count_by_status(batch_date)
    assert count == {"NOT_PROCESSABLE": 2}

    factories.PaymentStatusFactory(status=TransactionStatus.PENDING, payment=ps.payment)
    count = payment_queries.get_payment_count_by_status(batch_date)
    assert count == {"NOT_PROCESSABLE": 1, "PENDING": 1}


@pytest.mark.usefixtures("db_session")
class GetPaymentsByStatusTest:
    def test_without_batch_date(self):
        p1 = factories.PaymentFactory()
        p2 = factories.PaymentFactory()

        query = payment_queries.get_payments_by_status([TransactionStatus.PENDING])
        assert set(query.all()) == {p1, p2}

        factories.PaymentStatusFactory(status=TransactionStatus.NOT_PROCESSABLE, payment=p2)
        query = payment_queries.get_payments_by_status([TransactionStatus.PENDING])
        assert query.all() == [p1]
        query = payment_queries.get_payments_by_status([TransactionStatus.NOT_PROCESSABLE])
        assert query.all() == [p2]

    def test_with_specific_batch_date(self):
        batch_date = datetime.datetime.utcnow()
        query = payment_queries.get_payments_by_status([TransactionStatus.NOT_PROCESSABLE], batch_date)

        factories.PaymentFactory()  # not the same batch date
        assert query.count() == 0

        ps = factories.PaymentStatusFactory(status=TransactionStatus.PENDING, payment__batchDate=batch_date)
        assert query.count() == 0

        factories.PaymentStatusFactory(status=TransactionStatus.NOT_PROCESSABLE, payment=ps.payment)
        assert query.all() == [ps.payment]


@pytest.mark.usefixtures("db_session")
def test_group_by_iban_and_bic():
    factories.PaymentFactory(
        author="select-me",
        iban="iban1",
        bic="bic1",
        amount=10,
        recipientName="name1",
        recipientSiren="siren1",
        transactionLabel="label",
    )
    factories.PaymentFactory(
        author="select-me",
        iban="iban1",
        bic="bic2",
        amount=20,
        recipientName="name2",
        recipientSiren="siren2",
        transactionLabel="label",
    )
    factories.PaymentFactory(
        author="select-me",
        iban="iban1",
        bic="bic2",
        amount=40,
        recipientName="name2",
        recipientSiren="siren2",
        transactionLabel="label",
    )
    factories.PaymentFactory(author="ignored", iban="ignored", bic="ignored")

    query = Payment.query.filter_by(author="select-me")

    pairs = payment_queries.group_by_iban_and_bic(query)
    assert pairs == {
        ("iban1", "bic1", 10, "name1", "siren1", "label"),
        ("iban1", "bic2", 60, "name2", "siren2", "label"),
    }


@pytest.mark.usefixtures("db_session")
def test_group_by_venue():
    venue1 = offers_factories.VenueFactory(
        name="Venue 1",
        siret="siret1",
        managingOfferer__name="Offerer 1",
        managingOfferer__siren="siren1",
    )
    factories.PaymentFactory(
        booking__stock__offer__venue=venue1,
        author="",
        iban="iban1",
        bic="bic1",
        amount=10,
    )
    venue2 = offers_factories.VenueFactory(
        name="Venue 2",
        siret="siret2",
        managingOfferer__name="Offerer 2",
        managingOfferer__siren="siren2",
    )
    factories.PaymentFactory(
        booking__stock__offer__venue=venue2,
        author="",
        iban="iban2",
        bic="bic2",
        amount=20,
    )
    factories.PaymentFactory(
        booking__stock__offer__venue=venue2,
        author="",
        iban="iban2",
        bic="bic2",
        amount=40,
    )
    factories.PaymentFactory(author="ignored", iban="ignored", bic="ignored")

    query = Payment.query.filter_by(author="")

    pairs = payment_queries.group_by_venue(query)
    assert pairs == [
        (venue1.id, "Venue 1", "siret1", "Offerer 1", "siren1", "iban1", "bic1", 10),
        (venue2.id, "Venue 2", "siret2", "Offerer 2", "siren2", "iban2", "bic2", 60),
    ]
