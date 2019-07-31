from typing import List

from models import PcObject
from models.payment_status import TransactionStatus
from scripts.dashboard.finance_statistics import get_total_deposits, get_total_amount_spent, get_total_amount_to_pay, \
    query_get_top_20_offers_by_number_of_bookings
from tests.conftest import clean_database
from tests.test_utils import create_deposit, create_user, create_booking, create_stock, create_offer_with_thing_product, \
    create_venue, create_offerer, create_payment


class GetTotalDepositsTest:
    @clean_database
    def test_returns_0_if_no_deposits(self, app):
        # When
        total_deposits = get_total_deposits()

        # Then
        assert total_deposits == 0

    @clean_database
    def test_returns_1000_if_two_deposits(self, app):
        # Given
        user1 = create_user(email='test1@email.com')
        deposit1 = create_deposit(user1, amount=500)
        user2 = create_user(email='test2@email.com')
        deposit2 = create_deposit(user2, amount=500)

        PcObject.save(deposit1, deposit2)

        # When
        total_deposits = get_total_deposits()

        # Then
        assert total_deposits == 1000


class GetTotalAmountSpentTest:
    @clean_database
    def test_returns_0_if_no_bookings(self, app):
        # When
        total_amount_spent = get_total_amount_spent()

        # Then
        assert total_amount_spent == 0

    @clean_database
    def test_returns_20_if_two_booking_with_amount_10(self, app):
        # Given
        user1 = create_user(email='email1@test.com')
        user2 = create_user(email='email2@test.com')
        deposit1 = create_deposit(user1, amount=500)
        deposit2 = create_deposit(user2, amount=500)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(price=10, offer=offer)
        booking1 = create_booking(user1, stock, venue=venue)
        booking2 = create_booking(user2, stock, venue=venue)
        PcObject.save(booking1, booking2, deposit1, deposit2)

        # When
        total_amount_spent = get_total_amount_spent()

        # Then
        assert total_amount_spent == 20

    @clean_database
    def test_returns_10_if_two_booking_with_amount_10_and_one_cancelled(self, app):
        # Given
        user1 = create_user(email='email1@test.com')
        user2 = create_user(email='email2@test.com')
        deposit1 = create_deposit(user1, amount=500)
        deposit2 = create_deposit(user2, amount=500)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(price=10, offer=offer)
        booking1 = create_booking(user1, stock, venue=venue)
        booking2 = create_booking(user2, stock, venue=venue, is_cancelled=True)
        PcObject.save(booking1, booking2, deposit1, deposit2)

        # When
        total_amount_spent = get_total_amount_spent()

        # Then
        assert total_amount_spent == 10

    @clean_database
    def test_returns_20_if_one_booking_with_amount_10_and_quantity_2(self, app):
        # Given
        user = create_user(email='email1@test.com')
        deposit = create_deposit(user, amount=500)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(price=10, offer=offer)
        booking = create_booking(user, stock, venue=venue, quantity=2)
        PcObject.save(booking, deposit)

        # When
        total_amount_spent = get_total_amount_spent()

        # Then
        assert total_amount_spent == 20


class GetTotalAmountToPayTest:
    @clean_database
    def test_returns_0_if_no_payments(self, app):
        # When
        total_amount_to_pay = get_total_amount_to_pay()

        # Then
        assert total_amount_to_pay == 0

    @clean_database
    def test_returns_20_if_one_payment_with_amount_10_and_one_with_amount_5(self, app):
        # Given
        user1 = create_user(email='email1@test.com')
        user2 = create_user(email='email2@test.com')
        deposit1 = create_deposit(user1, amount=500)
        deposit2 = create_deposit(user2, amount=500)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(price=10, offer=offer)
        booking1 = create_booking(user1, stock, venue=venue)
        booking2 = create_booking(user2, stock, venue=venue)
        payment1 = create_payment(booking1, offerer, amount=5)
        payment2 = create_payment(booking2, offerer, amount=10)
        PcObject.save(payment1, payment2)

        # When
        total_amount_to_pay = get_total_amount_to_pay()

        # Then
        assert total_amount_to_pay == 15

    @clean_database
    def test_returns_0_if_last_payment_status_banned(self, app):
        # Given
        user = create_user(email='email@test.com')
        deposit = create_deposit(user, amount=500)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(price=10, offer=offer)
        booking = create_booking(user, stock, venue=venue)
        payment = create_payment(booking, offerer, amount=5, status=TransactionStatus.BANNED)
        PcObject.save(payment)

        # When
        total_amount_to_pay = get_total_amount_to_pay()

        # Then
        assert total_amount_to_pay == 0

    @clean_database
    def test_returns_5_if_amount_5_and_last_payment_status_not_banned(self, app):
        # Given
        user = create_user(email='email@test.com')
        deposit = create_deposit(user, amount=500)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(price=10, offer=offer)
        booking = create_booking(user, stock, venue=venue)
        payment = create_payment(booking, offerer, amount=5, status=TransactionStatus.BANNED)
        payment.setStatus(TransactionStatus.RETRY)
        PcObject.save(payment)

        # When
        total_amount_to_pay = get_total_amount_to_pay()

        # Then
        assert total_amount_to_pay == 5


class QueryGetTop20OffersByNumberOfBookingsTest:
    @clean_database
    def test_(self, app):
        # Given
        quantities = [14, 15, 16, 17, 18, 19, 20, 21, 22, 22, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        bookings = create_bookings_with_quantities(quantities)
        PcObject.save(*bookings)
        expected_counts = [
            ('8', 22, 0), ('9', 22, 0), ('7', 21, 0), ('6', 20, 0), ('5', 19, 0), ('4', 18, 0),
            ('3', 17, 0), ('2', 16, 0), ('1', 15, 0), ('0', 14, 0), ('23', 14, 0), ('22', 13, 0),
            ('21', 12, 0), ('20', 11, 0), ('19', 10, 0), ('18', 9, 0), ('17', 8, 0), ('16', 7, 0),
            ('15', 6, 0), ('14', 5, 0), ('13', 4, 0), ('12', 3, 0), ('11', 2, 0), ('10', 1, 0)
        ]

        # When
        bookings_counts = query_get_top_20_offers_by_number_of_bookings().fetchall()

        # Then
        print(bookings_counts)
        print(expected_counts)
        assert bookings_counts == expected_counts


def create_bookings_with_quantities(quantities: List[int]):
    siren = 111111111
    bookings = []
    for i, quantity in enumerate(quantities):
        offerer = create_offerer(siren=str(siren))
        venue = create_venue(offerer, siret=offerer.siren + '12345')
        offer = create_offer_with_thing_product(venue, thing_name=f'{i}')
        stock = create_stock(offer=offer, price=0, available=1000)
        user = create_user(email=f'{i}@mail.com')
        bookings.append(create_booking(user, stock, quantity=quantity))
        siren += 1
    return bookings
