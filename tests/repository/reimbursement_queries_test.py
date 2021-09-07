from datetime import date
from datetime import datetime
from datetime import timedelta
from decimal import Decimal

import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers.factories import OffererFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.payments import factories as payments_factories
from pcapi.core.users import factories as users_factories
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository.reimbursement_queries import find_all_offerer_payments
from pcapi.repository.reimbursement_queries import legacy_find_all_offerer_payments


today = date.today()
tomorrow = today + timedelta(days=1)
in_two_days = today + timedelta(days=2)
reimbursement_period = (today, in_two_days)


class FindAllOffererPaymentsTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_payment_info_with_error_status(self, app):
        # Given
        booking = bookings_factories.UsedBookingFactory()
        offerer = booking.stock.offer.venue.managingOfferer
        payment = payments_factories.PaymentFactory(
            booking=booking, transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019"
        )
        payments_factories.PaymentStatusFactory(
            payment=payment, status=TransactionStatus.ERROR, detail="Iban non fourni"
        )

        # When
        payments = find_all_offerer_payments(offerer.id, reimbursement_period)

        # Then
        assert len(payments) == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_payment_info_with_sent_status(self, app):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(lastName="User", firstName="Plus")
        stock = offers_factories.ThingStockFactory(
            offer__name="Test Book",
            offer__venue__managingOfferer__address="7 rue du livre",
            offer__venue__name="La petite librairie",
            offer__venue__address="123 rue de Paris",
            offer__venue__siret=12345678912345,
            price=10,
        )
        now = datetime.utcnow()
        booking = bookings_factories.UsedBookingFactory(user=beneficiary, stock=stock, dateUsed=now, token="ABCDEF")

        payment = payments_factories.PaymentFactory(
            amount=50,
            reimbursementRate=0.5,
            booking=booking,
            iban="CF13QSDFGH456789",
            transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019",
        )
        payments_factories.PaymentStatusFactory(
            payment=payment, status=TransactionStatus.ERROR, detail="Iban non fourni"
        )
        payments_factories.PaymentStatusFactory(payment=payment, status=TransactionStatus.RETRY, detail="All good")
        payments_factories.PaymentStatusFactory(payment=payment, status=TransactionStatus.SENT, detail="All good")

        # When
        payments = find_all_offerer_payments(stock.offer.venue.managingOfferer.id, reimbursement_period)

        # Then
        assert len(payments) == 1
        assert payments[0] == (
            "User",
            "Plus",
            "ABCDEF",
            now,
            1,
            Decimal("10.00"),
            "Test Book",
            "7 rue du livre",
            "La petite librairie",
            "12345678912345",
            "123 rue de Paris",
            Decimal("50.00"),
            Decimal("0.50"),
            "CF13QSDFGH456789",
            "pass Culture Pro - remboursement 1ère quinzaine 07-2019",
            TransactionStatus.SENT,
            "All good",
        )

    @pytest.mark.usefixtures("db_session")
    def test_should_return_last_matching_status_based_on_date_for_each_payment(self, app):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(lastName="User", firstName="Plus")
        stock = offers_factories.ThingStockFactory(
            offer__name="Test Book",
            offer__venue__managingOfferer__address="7 rue du livre",
            offer__venue__name="La petite librairie",
            offer__venue__address="123 rue de Paris",
            offer__venue__siret=12345678912345,
            price=10,
        )
        now = datetime.utcnow()
        booking1 = bookings_factories.UsedBookingFactory(user=beneficiary, stock=stock, dateUsed=now, token="ABCDEF")
        booking2 = bookings_factories.UsedBookingFactory(user=beneficiary, stock=stock, dateUsed=now, token="ABCDFE")

        payment = payments_factories.PaymentFactory(
            amount=50,
            reimbursementRate=0.5,
            booking=booking1,
            iban="CF13QSDFGH456789",
            transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019",
        )
        payments_factories.PaymentStatusFactory(payment=payment, status=TransactionStatus.RETRY, detail="Retry")
        payments_factories.PaymentStatusFactory(payment=payment, status=TransactionStatus.SENT, detail="All good")

        payment2 = payments_factories.PaymentFactory(
            amount=75,
            reimbursementRate=0.5,
            booking=booking2,
            iban="CF13QSDFGH456789",
            transactionLabel="pass Culture Pro - remboursement 2ème quinzaine 07-2019",
        )
        payments_factories.PaymentStatusFactory(
            payment=payment2, status=TransactionStatus.ERROR, detail="Iban non fourni"
        )
        payments_factories.PaymentStatusFactory(
            payment=payment2, status=TransactionStatus.SENT, detail="All realy good"
        )

        # When
        payments = find_all_offerer_payments(stock.offer.venue.managingOfferer.id, reimbursement_period)

        # Then
        assert len(payments) == 2
        assert payments[0] == (
            "User",
            "Plus",
            "ABCDFE",
            now,
            1,
            Decimal("10.00"),
            "Test Book",
            "7 rue du livre",
            "La petite librairie",
            "12345678912345",
            "123 rue de Paris",
            Decimal("75.00"),
            Decimal("0.50"),
            "CF13QSDFGH456789",
            "pass Culture Pro - remboursement 2ème quinzaine 07-2019",
            TransactionStatus.SENT,
            "All realy good",
        )
        assert payments[1] == (
            "User",
            "Plus",
            "ABCDEF",
            now,
            1,
            Decimal("10.00"),
            "Test Book",
            "7 rue du livre",
            "La petite librairie",
            "12345678912345",
            "123 rue de Paris",
            Decimal("50.00"),
            Decimal("0.50"),
            "CF13QSDFGH456789",
            "pass Culture Pro - remboursement 1ère quinzaine 07-2019",
            TransactionStatus.SENT,
            "All good",
        )

    @pytest.mark.usefixtures("db_session")
    def test_should_return_payments_from_multiple_venues(self, app):
        # Given
        offerer = OffererFactory()
        payments_factories.PaymentStatusFactory(
            payment__booking__stock__offer__venue__managingOfferer=offerer, status=TransactionStatus.SENT
        )
        payments_factories.PaymentStatusFactory(
            payment__booking__stock__offer__venue__managingOfferer=offerer, status=TransactionStatus.SENT
        )

        # When
        payments = find_all_offerer_payments(offerer.id, reimbursement_period)

        # Then
        assert len(payments) == 2

    @pytest.mark.usefixtures("db_session")
    def test_should_return_payments_filtered_by_venue(self, app):
        # Given
        offerer = OffererFactory()
        venue_1 = VenueFactory(managingOfferer=offerer)
        venue_2 = VenueFactory(managingOfferer=offerer)

        payment_1 = payments_factories.PaymentFactory(booking__stock__offer__venue=venue_1)
        payments_factories.PaymentStatusFactory(payment=payment_1, status=TransactionStatus.SENT)
        payment_2 = payments_factories.PaymentFactory(booking__stock__offer__venue=venue_2)
        payments_factories.PaymentStatusFactory(payment=payment_2, status=TransactionStatus.SENT)

        # When
        payments = find_all_offerer_payments(offerer.id, reimbursement_period, venue_1.id)

        # Then
        assert len(payments) == 1
        assert payments[0][2] == payment_1.booking.token
        assert payments[0][8] == venue_1.name

    @pytest.mark.usefixtures("db_session")
    def test_should_return_payments_filtered_by_payment_date(self, app):
        # Given
        tomorrow_at_nine = datetime.combine(tomorrow, datetime.min.time()) + timedelta(hours=9)
        offerer = OffererFactory()
        venue_1 = VenueFactory(managingOfferer=offerer)
        payment_1 = payments_factories.PaymentFactory(booking__stock__offer__venue=venue_1)
        payments_factories.PaymentStatusFactory(date=tomorrow_at_nine, payment=payment_1, status=TransactionStatus.SENT)
        payment_2 = payments_factories.PaymentFactory(booking__stock__offer__venue=venue_1)
        payments_factories.PaymentStatusFactory(date=in_two_days, payment=payment_2, status=TransactionStatus.SENT)

        # When
        payments = find_all_offerer_payments(offerer.id, (today, tomorrow))

        # Then
        assert len(payments) == 1
        assert payments[0][2] == payment_1.booking.token
        assert payments[0][8] == venue_1.name


class LegacyFindAllOffererPaymentsTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_payment_info_with_error_status(self, app):
        # Given
        stock = offers_factories.ThingStockFactory(price=10)
        now = datetime.utcnow()
        booking = bookings_factories.UsedBookingFactory(stock=stock, dateUsed=now, token="ABCDEF")
        payment = payments_factories.PaymentFactory(
            booking=booking, transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019"
        )
        payments_factories.PaymentStatusFactory(
            payment=payment, status=TransactionStatus.ERROR, detail="Iban non fourni"
        )

        # When
        payments = legacy_find_all_offerer_payments(stock.offer.venue.managingOfferer.id)

        # Then
        assert len(payments) == 1
        assert payments[0] == (
            "Doux",
            "Jeanne",
            "ABCDEF",
            now,
            1,
            Decimal("10.00"),
            stock.offer.name,
            "1 boulevard Poissonnière",
            stock.offer.venue.name,
            stock.offer.venue.siret,
            "1 boulevard Poissonnière",
            Decimal("10.00"),
            Decimal("1.00"),
            "CF13QSDFGH456789",
            "pass Culture Pro - remboursement 1ère quinzaine 07-2019",
            TransactionStatus.ERROR,
            "Iban non fourni",
        )

    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_payment_info_with_sent_status(self, app):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(lastName="User", firstName="Plus")
        stock = offers_factories.ThingStockFactory(
            offer__name="Test Book",
            offer__venue__managingOfferer__address="7 rue du livre",
            offer__venue__name="La petite librairie",
            offer__venue__address="123 rue de Paris",
            offer__venue__siret=12345678912345,
            price=10,
        )
        now = datetime.utcnow()
        booking = bookings_factories.UsedBookingFactory(user=beneficiary, stock=stock, dateUsed=now, token="ABCDEF")

        payment = payments_factories.PaymentFactory(
            amount=50,
            reimbursementRate=0.5,
            booking=booking,
            iban="CF13QSDFGH456789",
            transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019",
        )
        payments_factories.PaymentStatusFactory(
            payment=payment, status=TransactionStatus.ERROR, detail="Iban non fourni"
        )
        payments_factories.PaymentStatusFactory(payment=payment, status=TransactionStatus.RETRY, detail="All good")
        payments_factories.PaymentStatusFactory(payment=payment, status=TransactionStatus.SENT, detail="All good")

        # When
        payments = legacy_find_all_offerer_payments(stock.offer.venue.managingOfferer.id)

        # Then
        assert len(payments) == 1
        assert payments[0] == (
            "User",
            "Plus",
            "ABCDEF",
            now,
            1,
            Decimal("10.00"),
            "Test Book",
            "7 rue du livre",
            "La petite librairie",
            "12345678912345",
            "123 rue de Paris",
            Decimal("50.00"),
            Decimal("0.50"),
            "CF13QSDFGH456789",
            "pass Culture Pro - remboursement 1ère quinzaine 07-2019",
            TransactionStatus.SENT,
            "All good",
        )

    @pytest.mark.usefixtures("db_session")
    def test_should_return_last_matching_status_based_on_date_for_each_payment(self, app):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory(lastName="User", firstName="Plus")
        stock = offers_factories.ThingStockFactory(
            offer__name="Test Book",
            offer__venue__managingOfferer__address="7 rue du livre",
            offer__venue__name="La petite librairie",
            offer__venue__address="123 rue de Paris",
            offer__venue__siret=12345678912345,
            price=10,
        )
        now = datetime.utcnow()
        booking1 = bookings_factories.UsedBookingFactory(user=beneficiary, stock=stock, dateUsed=now, token="ABCDEF")
        booking2 = bookings_factories.UsedBookingFactory(user=beneficiary, stock=stock, dateUsed=now, token="ABCDFE")

        payment = payments_factories.PaymentFactory(
            amount=50,
            reimbursementRate=0.5,
            booking=booking1,
            iban="CF13QSDFGH456789",
            transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019",
        )
        payments_factories.PaymentStatusFactory(payment=payment, status=TransactionStatus.RETRY, detail="Retry")
        payments_factories.PaymentStatusFactory(payment=payment, status=TransactionStatus.SENT, detail="All good")

        payment2 = payments_factories.PaymentFactory(
            amount=75,
            reimbursementRate=0.5,
            booking=booking2,
            iban="CF13QSDFGH456789",
            transactionLabel="pass Culture Pro - remboursement 2ème quinzaine 07-2019",
        )
        payments_factories.PaymentStatusFactory(
            payment=payment2, status=TransactionStatus.ERROR, detail="Iban non fourni"
        )
        payments_factories.PaymentStatusFactory(
            payment=payment2, status=TransactionStatus.SENT, detail="All realy good"
        )

        # When
        payments = legacy_find_all_offerer_payments(stock.offer.venue.managingOfferer.id)

        # Then
        assert len(payments) == 2
        assert payments[0] == (
            "User",
            "Plus",
            "ABCDFE",
            now,
            1,
            Decimal("10.00"),
            "Test Book",
            "7 rue du livre",
            "La petite librairie",
            "12345678912345",
            "123 rue de Paris",
            Decimal("75.00"),
            Decimal("0.50"),
            "CF13QSDFGH456789",
            "pass Culture Pro - remboursement 2ème quinzaine 07-2019",
            TransactionStatus.SENT,
            "All realy good",
        )
        assert payments[1] == (
            "User",
            "Plus",
            "ABCDEF",
            now,
            1,
            Decimal("10.00"),
            "Test Book",
            "7 rue du livre",
            "La petite librairie",
            "12345678912345",
            "123 rue de Paris",
            Decimal("50.00"),
            Decimal("0.50"),
            "CF13QSDFGH456789",
            "pass Culture Pro - remboursement 1ère quinzaine 07-2019",
            TransactionStatus.SENT,
            "All good",
        )
