from datetime import datetime
from decimal import Decimal

import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offers import factories as offers_factories
from pcapi.core.payments import factories as payments_factories
from pcapi.core.users import factories as users_factories
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository.reimbursement_queries import find_all_offerer_payments


class FindAllOffererPaymentsTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_payment_info_with_error_status(self, app):
        # Given
        stock = offers_factories.ThingStockFactory(price=10)
        now = datetime.utcnow()
        booking = bookings_factories.BookingFactory(
            stock=stock, isUsed=True, status=BookingStatus.USED, dateUsed=now, token="ABCDEF"
        )
        payment = payments_factories.PaymentFactory(
            booking=booking, transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019"
        )
        payments_factories.PaymentStatusFactory(
            payment=payment, status=TransactionStatus.ERROR, detail="Iban non fourni"
        )

        # When
        payments = find_all_offerer_payments(stock.offer.venue.managingOfferer.id)

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
        user = users_factories.UserFactory(lastName="User", firstName="Plus")
        stock = offers_factories.ThingStockFactory(
            offer__name="Test Book",
            offer__venue__managingOfferer__address="7 rue du livre",
            offer__venue__name="La petite librairie",
            offer__venue__address="123 rue de Paris",
            offer__venue__siret=12345678912345,
            price=10,
        )
        now = datetime.utcnow()
        booking = bookings_factories.BookingFactory(user=user, stock=stock, isUsed=True, dateUsed=now, token="ABCDEF")

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
        payments = find_all_offerer_payments(stock.offer.venue.managingOfferer.id)

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
        user = users_factories.UserFactory(lastName="User", firstName="Plus")
        stock = offers_factories.ThingStockFactory(
            offer__name="Test Book",
            offer__venue__managingOfferer__address="7 rue du livre",
            offer__venue__name="La petite librairie",
            offer__venue__address="123 rue de Paris",
            offer__venue__siret=12345678912345,
            price=10,
        )
        now = datetime.utcnow()
        booking1 = bookings_factories.BookingFactory(user=user, stock=stock, isUsed=True, dateUsed=now, token="ABCDEF")
        booking2 = bookings_factories.BookingFactory(user=user, stock=stock, isUsed=True, dateUsed=now, token="ABCDFE")

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
        payments = find_all_offerer_payments(stock.offer.venue.managingOfferer.id)

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
