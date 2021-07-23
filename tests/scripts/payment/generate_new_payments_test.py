import datetime

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.payments.factories as payments_factories
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories
from pcapi.models.payment import Payment
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository import repository
from pcapi.scripts.payment.batch_steps import generate_new_payments


def get_pending_payments():
    return Payment.query.filter(Payment.statuses.any(status=TransactionStatus.PENDING))


def get_not_processable_payments():
    return Payment.query.filter(Payment.statuses.any(status=TransactionStatus.NOT_PROCESSABLE))


def total_amount(payment_query):
    return sum(amount for amount, in payment_query.with_entities(Payment.amount).all())


class GenerateNewPaymentsTest:
    @pytest.mark.usefixtures("db_session")
    def test_records_new_payment_lines_in_database(self):
        # Given
        cutoff = datetime.datetime.now()
        before_cutoff = cutoff - datetime.timedelta(days=1)

        beneficiary = users_factories.BeneficiaryFactory(email="user@example.com")
        offerer = offers_factories.OffererFactory()
        offer = offers_factories.ThingOfferFactory(venue__managingOfferer=offerer)
        paying_stock = offers_factories.ThingStockFactory(offer=offer)
        free_stock = offers_factories.ThingStockFactory(offer=offer, price=0)
        bookings_factories.BookingFactory(
            user=beneficiary, stock=paying_stock, isUsed=True, status=BookingStatus.USED, dateUsed=before_cutoff
        )
        bookings_factories.BookingFactory(
            user=beneficiary, stock=paying_stock, isUsed=True, status=BookingStatus.USED, dateUsed=before_cutoff
        )
        bookings_factories.BookingFactory(
            user=beneficiary, stock=free_stock, isUsed=True, status=BookingStatus.USED, dateUsed=before_cutoff
        )
        bookings_factories.BookingFactory(
            user=beneficiary, stock=free_stock, isUsed=True, status=BookingStatus.USED, dateUsed=before_cutoff
        )
        bookings_factories.BookingFactory(
            user=beneficiary, stock=paying_stock, isUsed=True, status=BookingStatus.USED, dateUsed=cutoff
        )

        payment_message = payments_factories.PaymentMessageFactory(name="ABCD123")
        payments_factories.PaymentFactory(paymentMessage=payment_message)

        initial_payment_count = Payment.query.count()

        # When
        n_queries = 1  # get_venue_ids_to_reimburse()
        n_queries += 1  # fetch custom reimbursement rules
        n_queries += 1  # find_bookings_eligible_for_payment_for_venue()
        n_queries += 1  # insert payments
        n_queries += 1  # release savepoint (commit)
        n_queries += 1  # insert PENDING payment statuses
        n_queries += 1  # release savepoint (commit)
        n_queries += 1  # insert NOT_PROCESSABLE payment statuses
        n_queries += 1  # release savepoint (commit)
        with assert_num_queries(n_queries):
            generate_new_payments(cutoff, batch_date=datetime.datetime.now())

        # Then
        assert Payment.query.count() - initial_payment_count == 2

    @pytest.mark.usefixtures("db_session")
    def test_creates_pending_and_not_processable_payments(self):
        # Given
        cutoff = datetime.datetime.now()
        before_cutoff = cutoff - datetime.timedelta(days=1)

        beneficiary = users_factories.BeneficiaryFactory(email="user@example.com")
        offerer1 = offers_factories.OffererFactory(siren="123456789")
        offerer2 = offers_factories.OffererFactory(siren="987654321")
        offers_factories.BankInformationFactory(bic="BDFEFR2LCCB", iban="FR7630006000011234567890189", offerer=offerer1)
        venue1 = offers_factories.VenueFactory(managingOfferer=offerer1, siret="12345678912345")
        venue2 = offers_factories.VenueFactory(managingOfferer=offerer2, siret="98765432154321")
        offer1 = offers_factories.ThingOfferFactory(venue=venue1)
        offer2 = offers_factories.ThingOfferFactory(venue=venue2)

        paying_stock1 = offers_factories.ThingStockFactory(offer=offer1)
        paying_stock2 = offers_factories.ThingStockFactory(offer=offer2)
        free_stock1 = offers_factories.ThingStockFactory(offer=offer1, price=0)
        bookings_factories.BookingFactory(user=beneficiary, stock=paying_stock1, isUsed=True, dateUsed=before_cutoff)
        bookings_factories.BookingFactory(user=beneficiary, stock=paying_stock1, isUsed=True, dateUsed=before_cutoff)
        bookings_factories.BookingFactory(user=beneficiary, stock=paying_stock2, isUsed=True, dateUsed=before_cutoff)
        bookings_factories.BookingFactory(user=beneficiary, stock=free_stock1, isUsed=True, dateUsed=before_cutoff)

        # When
        generate_new_payments(cutoff, batch_date=datetime.datetime.now())

        # Then
        assert get_pending_payments().count() == 2
        assert get_not_processable_payments().count() == 1

    @pytest.mark.usefixtures("db_session")
    def test_reimburses_offerer_if_he_has_more_than_20000_euros_in_bookings_on_several_venues(self):
        # Given
        cutoff = datetime.datetime.now()
        before_cutoff = cutoff - datetime.timedelta(days=1)

        beneficiary = users_factories.BeneficiaryFactory(email="user@example.com")
        offerer1 = offers_factories.OffererFactory(siren="123456789")
        offers_factories.BankInformationFactory(bic="BDFEFR2LCCB", iban="FR7630006000011234567890189", offerer=offerer1)
        venue1 = offers_factories.VenueFactory(managingOfferer=offerer1, siret="12345678912345")
        venue2 = offers_factories.VenueFactory(managingOfferer=offerer1, siret="98765432154321")
        venue3 = offers_factories.VenueFactory(managingOfferer=offerer1, siret="98123432154321")
        offer1 = offers_factories.ThingOfferFactory(venue=venue1)
        offer2 = offers_factories.ThingOfferFactory(venue=venue2)
        offer3 = offers_factories.ThingOfferFactory(venue=venue3)

        paying_stock1 = offers_factories.ThingStockFactory(offer=offer1, price=10000)
        paying_stock2 = offers_factories.ThingStockFactory(offer=offer2, price=10000)
        paying_stock3 = offers_factories.ThingStockFactory(offer=offer3, price=10000)
        offers_factories.ThingStockFactory(offer=offer1, price=0)

        beneficiary.deposit.amount = 50000
        repository.save(beneficiary.deposit)

        bookings_factories.BookingFactory(
            user=beneficiary, stock=paying_stock1, isUsed=True, dateUsed=before_cutoff, quantity=1
        )
        bookings_factories.BookingFactory(
            user=beneficiary, stock=paying_stock2, isUsed=True, dateUsed=before_cutoff, quantity=1
        )
        bookings_factories.BookingFactory(
            user=beneficiary, stock=paying_stock3, isUsed=True, dateUsed=before_cutoff, quantity=1
        )

        # When
        generate_new_payments(cutoff, batch_date=datetime.datetime.now())

        # Then
        pending = get_pending_payments()
        assert pending.count() == 3
        assert total_amount(pending) == 30000
        assert get_not_processable_payments().count() == 0

    @pytest.mark.usefixtures("db_session")
    def test_reimburses_offerer_with_degressive_rate_for_venues_with_bookings_exceeding_20000_euros(self):
        # Given
        cutoff = datetime.datetime.now()
        before_cutoff = cutoff - datetime.timedelta(days=1)

        beneficiary = users_factories.BeneficiaryFactory(email="user@example.com")
        offerer1 = offers_factories.OffererFactory(siren="123456789")
        offers_factories.BankInformationFactory(bic="BDFEFR2LCCB", iban="FR7630006000011234567890189", offerer=offerer1)
        venue1 = offers_factories.VenueFactory(managingOfferer=offerer1, siret="12345678912345")
        venue2 = offers_factories.VenueFactory(managingOfferer=offerer1, siret="98765432154321")
        venue3 = offers_factories.VenueFactory(managingOfferer=offerer1, siret="98123432154321")
        offer1 = offers_factories.ThingOfferFactory(venue=venue1)
        offer2 = offers_factories.ThingOfferFactory(venue=venue2)
        offer3 = offers_factories.ThingOfferFactory(venue=venue3)

        paying_stock1 = offers_factories.ThingStockFactory(offer=offer1, price=10000)
        paying_stock2 = offers_factories.ThingStockFactory(offer=offer2, price=10000)
        paying_stock3 = offers_factories.ThingStockFactory(offer=offer3, price=30000)
        offers_factories.ThingStockFactory(offer=offer1, price=0)

        beneficiary.deposit.amount = 50000
        repository.save(beneficiary.deposit)

        bookings_factories.BookingFactory(
            user=beneficiary, stock=paying_stock1, isUsed=True, dateUsed=before_cutoff, quantity=1
        )
        bookings_factories.BookingFactory(
            user=beneficiary, stock=paying_stock2, isUsed=True, dateUsed=before_cutoff, quantity=1
        )
        bookings_factories.BookingFactory(
            user=beneficiary, stock=paying_stock3, isUsed=True, dateUsed=before_cutoff, quantity=1
        )

        # When
        generate_new_payments(cutoff, batch_date=datetime.datetime.now())

        # Then
        pending = get_pending_payments()
        assert pending.count() == 3
        assert total_amount(pending) == 48500
        assert get_not_processable_payments().count() == 0

    @pytest.mark.usefixtures("db_session")
    def test_full_reimburses_book_product_when_bookings_are_below_20000_euros(self):
        # Given
        cutoff = datetime.datetime.now()
        before_cutoff = cutoff - datetime.timedelta(days=1)

        beneficiary = users_factories.BeneficiaryFactory(email="user@example.com")
        offerer1 = offers_factories.OffererFactory(siren="123456789")
        offers_factories.BankInformationFactory(bic="BDFEFR2LCCB", iban="FR7630006000011234567890189", offerer=offerer1)
        venue1 = offers_factories.VenueFactory(managingOfferer=offerer1, siret="12345678912345")
        venue2 = offers_factories.VenueFactory(managingOfferer=offerer1, siret="98765432154321")
        offer1 = offers_factories.ThingOfferFactory(venue=venue1)
        offer2 = offers_factories.ThingOfferFactory(venue=venue2)

        paying_stock1 = offers_factories.ThingStockFactory(offer=offer1, price=10000)
        paying_stock2 = offers_factories.ThingStockFactory(offer=offer2, price=19990)

        offers_factories.ThingStockFactory(offer=offer1, price=0)

        beneficiary.deposit.amount = 50000
        repository.save(beneficiary.deposit)

        bookings_factories.BookingFactory(
            user=beneficiary, stock=paying_stock1, isUsed=True, dateUsed=before_cutoff, quantity=1
        )
        bookings_factories.BookingFactory(
            user=beneficiary, stock=paying_stock2, isUsed=True, dateUsed=before_cutoff, quantity=1
        )

        # When
        generate_new_payments(cutoff, batch_date=datetime.datetime.now())

        # Then
        pending = get_pending_payments()
        assert pending.count() == 2
        assert total_amount(pending) == 29990
        assert get_not_processable_payments().count() == 0

    @pytest.mark.usefixtures("db_session")
    def test_reimburses_95_percent_for_book_product_when_bookings_exceed_20000_euros(self):
        # Given
        cutoff = datetime.datetime.now()
        before_cutoff = cutoff - datetime.timedelta(days=1)

        beneficiary = users_factories.BeneficiaryFactory(email="user@example.com")
        offerer1 = offers_factories.OffererFactory(siren="123456789")
        offers_factories.BankInformationFactory(bic="BDFEFR2LCCB", iban="FR7630006000011234567890189", offerer=offerer1)
        venue1 = offers_factories.VenueFactory(managingOfferer=offerer1, siret="12345678912345")
        venue2 = offers_factories.VenueFactory(managingOfferer=offerer1, siret="98765432154321")
        venue3 = offers_factories.VenueFactory(managingOfferer=offerer1, siret="98123432154321")
        offer1 = offers_factories.ThingOfferFactory(venue=venue1)
        offer2 = offers_factories.ThingOfferFactory(venue=venue2)
        offer3 = offers_factories.ThingOfferFactory(venue=venue3)

        paying_stock1 = offers_factories.ThingStockFactory(offer=offer1, price=10000)
        paying_stock2 = offers_factories.ThingStockFactory(offer=offer2, price=10000)
        paying_stock3 = offers_factories.ThingStockFactory(offer=offer3, price=30000)
        offers_factories.ThingStockFactory(offer=offer1, price=0)

        beneficiary.deposit.amount = 50000
        repository.save(beneficiary.deposit)

        bookings_factories.BookingFactory(
            user=beneficiary, stock=paying_stock1, isUsed=True, dateUsed=before_cutoff, quantity=1
        )
        bookings_factories.BookingFactory(
            user=beneficiary, stock=paying_stock2, isUsed=True, dateUsed=before_cutoff, quantity=1
        )
        bookings_factories.BookingFactory(
            user=beneficiary, stock=paying_stock3, isUsed=True, dateUsed=before_cutoff, quantity=1
        )

        # When
        generate_new_payments(cutoff, batch_date=datetime.datetime.now())

        # Then
        pending = get_pending_payments()
        assert pending.count() == 3
        assert total_amount(pending) == 48500
        assert get_not_processable_payments().count() == 0

    @pytest.mark.usefixtures("db_session")
    def test_reimburses_95_percent_for_book_product_when_bookings_exceed_40000_euros(self):
        # Given
        cutoff = datetime.datetime.now()
        before_cutoff = cutoff - datetime.timedelta(days=1)

        beneficiary = users_factories.BeneficiaryFactory(email="user@example.com")
        offerer1 = offers_factories.OffererFactory(siren="123456789")
        offers_factories.BankInformationFactory(bic="BDFEFR2LCCB", iban="FR7630006000011234567890189", offerer=offerer1)
        venue1 = offers_factories.VenueFactory(managingOfferer=offerer1, siret="12345678912345")
        venue2 = offers_factories.VenueFactory(managingOfferer=offerer1, siret="98765432154321")
        venue3 = offers_factories.VenueFactory(managingOfferer=offerer1, siret="98123432154321")
        product = offers_factories.ThingProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        offer1 = offers_factories.ThingOfferFactory(venue=venue1, product=product)
        offer2 = offers_factories.ThingOfferFactory(venue=venue2, product=product)
        offer3 = offers_factories.ThingOfferFactory(venue=venue3, product=product)

        paying_stock1 = offers_factories.ThingStockFactory(offer=offer1, price=10000)
        paying_stock2 = offers_factories.ThingStockFactory(offer=offer2, price=10000)
        paying_stock3 = offers_factories.ThingStockFactory(offer=offer3, price=50000)
        offers_factories.ThingStockFactory(offer=offer1, price=0)

        beneficiary.deposit.amount = 80000
        repository.save(beneficiary.deposit)

        bookings_factories.BookingFactory(
            user=beneficiary, stock=paying_stock1, isUsed=True, dateUsed=before_cutoff, quantity=1
        )
        bookings_factories.BookingFactory(
            user=beneficiary, stock=paying_stock2, isUsed=True, dateUsed=before_cutoff, quantity=1
        )
        bookings_factories.BookingFactory(
            user=beneficiary, stock=paying_stock3, isUsed=True, dateUsed=before_cutoff, quantity=1
        )

        # When
        generate_new_payments(cutoff, batch_date=datetime.datetime.now())

        # Then
        pending = get_pending_payments()
        assert pending.count() == 3
        assert total_amount(pending) == 67500
        assert get_not_processable_payments().count() == 0

    @pytest.mark.usefixtures("db_session")
    def test_reimburses_95_percent_for_book_product_when_bookings_exceed_100000_euros(self):
        # Given
        cutoff = datetime.datetime.now()
        before_cutoff = cutoff - datetime.timedelta(days=1)

        beneficiary = users_factories.BeneficiaryFactory(email="user@example.com")
        offerer1 = offers_factories.OffererFactory(siren="123456789")
        offers_factories.BankInformationFactory(bic="BDFEFR2LCCB", iban="FR7630006000011234567890189", offerer=offerer1)
        venue1 = offers_factories.VenueFactory(managingOfferer=offerer1, siret="12345678912345")
        venue2 = offers_factories.VenueFactory(managingOfferer=offerer1, siret="98765432154321")
        venue3 = offers_factories.VenueFactory(managingOfferer=offerer1, siret="98123432154321")
        product = offers_factories.ThingProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        offer1 = offers_factories.ThingOfferFactory(venue=venue1, product=product)
        offer2 = offers_factories.ThingOfferFactory(venue=venue2, product=product)
        offer3 = offers_factories.ThingOfferFactory(venue=venue3, product=product)

        paying_stock1 = offers_factories.ThingStockFactory(offer=offer1, price=10000)
        paying_stock2 = offers_factories.ThingStockFactory(offer=offer2, price=10000)
        paying_stock3 = offers_factories.ThingStockFactory(offer=offer3, price=100000)
        offers_factories.ThingStockFactory(offer=offer1, price=0)

        beneficiary.deposit.amount = 120000
        repository.save(beneficiary.deposit)

        bookings_factories.BookingFactory(
            user=beneficiary, stock=paying_stock1, isUsed=True, dateUsed=before_cutoff, quantity=1
        )
        bookings_factories.BookingFactory(
            user=beneficiary, stock=paying_stock2, isUsed=True, dateUsed=before_cutoff, quantity=1
        )
        bookings_factories.BookingFactory(
            user=beneficiary, stock=paying_stock3, isUsed=True, dateUsed=before_cutoff, quantity=1
        )

        # When
        generate_new_payments(cutoff, batch_date=datetime.datetime.now())

        # Then
        pending = get_pending_payments()
        assert pending.count() == 3
        assert total_amount(pending) == 115000
        assert get_not_processable_payments().count() == 0

    @pytest.mark.usefixtures("db_session")
    def test_use_custom_reimbursement_rule(self):
        offer = offers_factories.DigitalOfferFactory()
        offers_factories.BankInformationFactory(venue=offer.venue, iban="iban1", bic="bic1")
        bookings_factories.BookingFactory(
            amount=10, quantity=2, isUsed=True, dateUsed=datetime.datetime.now(), stock__offer=offer
        )
        rule = payments_factories.CustomReimbursementRuleFactory(offer=offer, amount=7)

        cutoff = batch_date = datetime.datetime.now()
        generate_new_payments(cutoff, batch_date)

        payment = Payment.query.one()
        assert payment.amount == 14  # 2 (booking.quantity) * 7 (Rule.amount)
        assert payment.customReimbursementRule == rule
