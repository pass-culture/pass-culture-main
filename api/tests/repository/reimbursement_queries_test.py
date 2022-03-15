from datetime import date
from datetime import datetime
from datetime import timedelta
from decimal import Decimal

import pytest

from pcapi.core.bookings import factories as bookings_factories
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers.factories import OffererFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.users import factories as users_factories
from pcapi.repository.reimbursement_queries import find_all_offerer_payments


today = date.today()
tomorrow = today + timedelta(days=1)
in_two_days = today + timedelta(days=2)
reimbursement_period = (today, in_two_days)


@pytest.mark.usefixtures("db_session")
class FindAllOffererPaymentsTest:
    def test_should_not_return_payment_info_with_error_status(self, app):
        # Given
        booking = bookings_factories.UsedBookingFactory()
        offerer = booking.offerer
        payment = finance_factories.PaymentFactory(
            booking=booking, transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019"
        )
        finance_factories.PaymentStatusFactory(
            payment=payment,
            status=finance_models.TransactionStatus.ERROR,
            detail="Iban non fourni",
        )

        # When
        payments = find_all_offerer_payments(offerer.id, reimbursement_period)

        # Then
        assert len(payments) == 0

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
        booking = bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user=beneficiary, stock=stock, dateUsed=now, token="ABCDEF"
        )

        payment = finance_factories.PaymentFactory(
            amount=50,
            reimbursementRate=0.5,
            booking=booking,
            iban="CF13QSDFGH456789",
            transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019",
        )
        finance_factories.PaymentStatusFactory(
            payment=payment,
            status=finance_models.TransactionStatus.ERROR,
            detail="Iban non fourni",
        )
        finance_factories.PaymentStatusFactory(
            payment=payment,
            status=finance_models.TransactionStatus.RETRY,
            detail="All good",
        )
        finance_factories.PaymentStatusFactory(
            payment=payment,
            status=finance_models.TransactionStatus.SENT,
            detail="All good",
        )

        # When
        payments = find_all_offerer_payments(stock.offer.venue.managingOfferer.id, reimbursement_period)

        # Then
        assert len(payments) == 1
        expected_elements = (
            "User",
            "Plus",
            "ABCDEF",
            now,
            1,
            Decimal("10.00"),
            "Test Book",
            False,
            "7 rue du livre",
            "La petite librairie",
            "12345678912345",
            "123 rue de Paris",
            Decimal("50.00"),
            Decimal("0.50"),
            "CF13QSDFGH456789",
            "pass Culture Pro - remboursement 1ère quinzaine 07-2019",
        )

        assert set(expected_elements).issubset(set(payments[0]))

    def test_should_return_one_payment_info_with_sent_status_when_offer_educational(self, app):
        # Given
        now = datetime.utcnow()
        educational_booking = bookings_factories.UsedEducationalBookingFactory(
            educationalBooking__educationalRedactor__firstName="Dominique",
            educationalBooking__educationalRedactor__lastName="Leprof",
            dateUsed=now,
            token="ABCDEF",
            quantity=5,
            amount=50,
            stock__price=10,
        )

        payment = finance_factories.PaymentFactory(
            amount=50,
            reimbursementRate=1,
            booking=educational_booking,
            iban="CF13QSDFGH456789",
            transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019",
        )
        finance_factories.PaymentStatusFactory(
            payment=payment,
            status=finance_models.TransactionStatus.ERROR,
            detail="Iban non fourni",
        )
        finance_factories.PaymentStatusFactory(
            payment=payment,
            status=finance_models.TransactionStatus.RETRY,
            detail="All good",
        )
        finance_factories.PaymentStatusFactory(
            payment=payment,
            status=finance_models.TransactionStatus.SENT,
            detail="All good",
        )

        # When
        payments = find_all_offerer_payments(
            educational_booking.stock.offer.venue.managingOfferer.id, reimbursement_period
        )

        # Then
        assert len(payments) == 1
        assert payments[0] == (
            None,
            None,
            "Dominique",
            "Leprof",
            "ABCDEF",
            now,
            educational_booking.quantity,
            educational_booking.amount,
            educational_booking.stock.offer.name,
            educational_booking.stock.offer.isEducational,
            educational_booking.stock.offer.venue.managingOfferer.address,
            educational_booking.stock.offer.venue.name,
            educational_booking.stock.offer.venue.siret,
            educational_booking.stock.offer.venue.address,
            Decimal("50.00"),
            Decimal("1.00"),
            "CF13QSDFGH456789",
            "pass Culture Pro - remboursement 1ère quinzaine 07-2019",
        )

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
        booking1 = bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user=beneficiary, stock=stock, dateUsed=now, token="ABCDEF"
        )
        booking2 = bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user=beneficiary, stock=stock, dateUsed=now, token="ABCDFE"
        )

        payment = finance_factories.PaymentFactory(
            amount=50,
            reimbursementRate=0.5,
            booking=booking1,
            iban="CF13QSDFGH456789",
            transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019",
        )
        finance_factories.PaymentStatusFactory(
            payment=payment, status=finance_models.TransactionStatus.RETRY, detail="Retry"
        )
        finance_factories.PaymentStatusFactory(
            payment=payment, status=finance_models.TransactionStatus.SENT, detail="All good"
        )

        payment2 = finance_factories.PaymentFactory(
            amount=75,
            reimbursementRate=0.5,
            booking=booking2,
            iban="CF13QSDFGH456789",
            transactionLabel="pass Culture Pro - remboursement 2ème quinzaine 07-2019",
        )
        finance_factories.PaymentStatusFactory(
            payment=payment2, status=finance_models.TransactionStatus.ERROR, detail="Iban non fourni"
        )
        finance_factories.PaymentStatusFactory(
            payment=payment2, status=finance_models.TransactionStatus.SENT, detail="All realy good"
        )

        # When
        payments = find_all_offerer_payments(stock.offer.venue.managingOfferer.id, reimbursement_period)

        # Then
        assert len(payments) == 2
        assert payments[0] == (
            "User",
            "Plus",
            None,
            None,
            "ABCDFE",
            now,
            1,
            Decimal("10.00"),
            "Test Book",
            False,
            "7 rue du livre",
            "La petite librairie",
            "12345678912345",
            "123 rue de Paris",
            Decimal("75.00"),
            Decimal("0.50"),
            "CF13QSDFGH456789",
            "pass Culture Pro - remboursement 2ème quinzaine 07-2019",
        )
        assert payments[1] == (
            "User",
            "Plus",
            None,
            None,
            "ABCDEF",
            now,
            1,
            Decimal("10.00"),
            "Test Book",
            False,
            "7 rue du livre",
            "La petite librairie",
            "12345678912345",
            "123 rue de Paris",
            Decimal("50.00"),
            Decimal("0.50"),
            "CF13QSDFGH456789",
            "pass Culture Pro - remboursement 1ère quinzaine 07-2019",
        )

    def test_should_return_payments_from_multiple_venues(self, app):
        # Given
        offerer = OffererFactory()
        finance_factories.PaymentStatusFactory(
            payment__booking__stock__offer__venue__managingOfferer=offerer, status=finance_models.TransactionStatus.SENT
        )
        finance_factories.PaymentStatusFactory(
            payment__booking__stock__offer__venue__managingOfferer=offerer, status=finance_models.TransactionStatus.SENT
        )

        # When
        payments = find_all_offerer_payments(offerer.id, reimbursement_period)

        # Then
        assert len(payments) == 2

    def test_should_return_payments_filtered_by_venue(self, app):
        # Given
        offerer = OffererFactory()
        venue_1 = VenueFactory(managingOfferer=offerer)
        venue_2 = VenueFactory(managingOfferer=offerer)

        payment_1 = finance_factories.PaymentFactory(booking__stock__offer__venue=venue_1)
        finance_factories.PaymentStatusFactory(payment=payment_1, status=finance_models.TransactionStatus.SENT)
        payment_2 = finance_factories.PaymentFactory(booking__stock__offer__venue=venue_2)
        finance_factories.PaymentStatusFactory(payment=payment_2, status=finance_models.TransactionStatus.SENT)

        # When
        payments = find_all_offerer_payments(offerer.id, reimbursement_period, venue_1.id)

        # Then
        assert len(payments) == 1
        assert payment_1.booking.token in payments[0]
        assert venue_1.name in payments[0]

    def test_should_return_payments_filtered_by_payment_date(self, app):
        # Given
        tomorrow_at_nine = datetime.combine(tomorrow, datetime.min.time()) + timedelta(hours=9)
        offerer = OffererFactory()
        venue_1 = VenueFactory(managingOfferer=offerer)
        payment_1 = finance_factories.PaymentFactory(booking__stock__offer__venue=venue_1)
        finance_factories.PaymentStatusFactory(
            date=tomorrow_at_nine, payment=payment_1, status=finance_models.TransactionStatus.SENT
        )
        payment_2 = finance_factories.PaymentFactory(booking__stock__offer__venue=venue_1)
        finance_factories.PaymentStatusFactory(
            date=in_two_days, payment=payment_2, status=finance_models.TransactionStatus.SENT
        )

        # When
        payments = find_all_offerer_payments(offerer.id, (today, tomorrow))

        # Then
        assert len(payments) == 1
        assert payment_1.booking.token in payments[0]
        assert venue_1.name in payments[0]

    # FIXME (dbaty, 2022-03-15): once we have Pricing and Cashflow for
    # pre-2022 payments, we can rename and update this test. Some
    # tests above could be updated, some could be removed if they
    # don't make sense.
    def test_with_new_models(self):
        stock = offers_factories.ThingStockFactory(
            offer__name="Test Book",
            offer__venue__managingOfferer__address="7 rue du livre",
            offer__venue__name="La petite librairie",
            offer__venue__address="123 rue de Paris",
            offer__venue__siret=12345678912345,
            offer__venue__businessUnit__bankAccount__iban="CF13QSDFGH456789",
            price=10,
        )
        booking = bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user__lastName="Doe",
            individualBooking__user__firstName="Jane",
            stock=stock,
            token="ABCDEF",
        )

        # Create an old-style payment
        payment = finance_factories.PaymentFactory(
            amount=9.5,
            reimbursementRate=0.95,
            booking=booking,
            iban="CF13QSDFGH456789",
            transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019",
        )
        finance_factories.PaymentStatusFactory(
            payment=payment,
            status=finance_models.TransactionStatus.SENT,
        )

        # Create a new-style pricing on the same booking. In real life
        # we cannot have a booking linked to both sets of models, but
        # here it's useful because we can test that the data is the
        # same.
        finance_factories.PricingFactory(
            booking=booking,
            amount=-9500,
            standardRule="Remboursement à 95% au dessus de 20 000 € pour les livres",
            status=finance_models.PricingStatus.VALIDATED,
        )
        finance_api.generate_cashflows(datetime.utcnow())
        finance_models.Pricing.query.update(
            {"status": finance_models.PricingStatus.INVOICED},
            synchronize_session=False,
        )

        payments = find_all_offerer_payments(booking.offerer.id, reimbursement_period)

        expected_in_both = {
            "user_lastName": "Doe",
            "user_firstName": "Jane",
            "redactor_firstname": None,
            "redactor_lastname": None,
            "booking_token": "ABCDEF",
            "booking_dateUsed": booking.dateUsed,
            "booking_quantity": 1,
            "booking_amount": Decimal("10.00"),
            "offer_name": "Test Book",
            "offer_is_educational": False,
            "offerer_address": "7 rue du livre",
            "venue_name": "La petite librairie",
            "venue_siret": "12345678912345",
            "venue_address": "123 rue de Paris",
            "iban": "CF13QSDFGH456789",
        }
        specific_for_payment = {
            "amount": Decimal("9.50"),
            "reimbursement_rate": Decimal("0.95"),
            "transactionLabel": "pass Culture Pro - remboursement 1ère quinzaine 07-2019",
        }
        specific_for_pricing = {
            "amount": Decimal("9500"),
            "rule_name": "Remboursement à 95% au dessus de 20 000 € pour les livres",
            "rule_id": None,
            "cashflow_date": booking.pricings[0].cashflows[0].creationDate,
        }

        missing_for_payment = (set(expected_in_both.keys()) | set(specific_for_payment.keys())).symmetric_difference(
            set(payments[1]._asdict())
        )
        assert missing_for_payment == set()
        for attr, expected in expected_in_both.items():
            assert getattr(payments[1], attr) == expected
        for attr, expected in specific_for_payment.items():
            assert getattr(payments[1], attr) == expected, f"wrong {attr}"

        missing_for_pricing = (set(expected_in_both.keys()) | set(specific_for_pricing.keys())).symmetric_difference(
            set(payments[0]._asdict())
        )
        assert missing_for_pricing == set()
        for attr, expected in expected_in_both.items():
            assert getattr(payments[0], attr) == expected
        for attr, expected in specific_for_pricing.items():
            assert getattr(payments[0], attr) == expected
