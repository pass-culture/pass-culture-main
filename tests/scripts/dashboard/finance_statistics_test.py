from typing import List

import pandas

from models import PcObject
from models.payment_status import TransactionStatus
from scripts.dashboard.finance_statistics import get_total_deposits, get_total_amount_spent, get_total_amount_to_pay, \
    _query_get_top_20_offers_by_number_of_bookings, get_top_20_offers_table, \
    _query_get_top_20_offerers_by_number_of_bookings, get_top_20_offerers_table_by_number_of_bookings, \
    _query_get_top_20_offerers_by_booking_amounts, get_top_20_offerers_by_amount_table
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

    @clean_database
    def test_returns_500_if_two_deposits_but_filtered_by_departement(self, app):
        # Given
        user1 = create_user(email='test1@email.com', departement_code='42')
        deposit1 = create_deposit(user1, amount=500)
        user2 = create_user(email='test2@email.com', departement_code='95')
        deposit2 = create_deposit(user2, amount=500)

        PcObject.save(deposit1, deposit2)

        # When
        total_deposits = get_total_deposits('95')

        # Then
        assert total_deposits == 500


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

    @clean_database
    def test_returns_20_if_two_bookings_but_only_one_the_filtered_departement(self, app):
        # Given
        user67 = create_user(email='email67@test.com', departement_code='67')
        create_deposit(user67, amount=500)
        user89 = create_user(email='email89@test.com', departement_code='89')
        create_deposit(user89, amount=500)

        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(price=15, offer=offer)
        booking_in_67 = create_booking(user67, stock, venue=venue)
        booking_in_89 = create_booking(user89, stock, venue=venue)
        PcObject.save(booking_in_67, booking_in_89, user67, user89)

        # When
        total_amount_spent = get_total_amount_spent('67')

        # Then
        assert total_amount_spent == 15


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

    @clean_database
    def test_returns_only_payment_total_by_department(self, app):
        # Given
        offerer = create_offerer(siren='111111111')
        venue_in_35 = create_venue(offerer, postal_code='35238', siret='11111111100001')
        venue_in_78 = create_venue(offerer, postal_code='78490', siret='11111111100002')
        offer_in_35 = create_offer_with_thing_product(venue_in_35)
        offer_in_78 = create_offer_with_thing_product(venue_in_78)
        stock_in_35 = create_stock(price=20, offer=offer_in_35)
        stock_in_78 = create_stock(price=10, offer=offer_in_78)

        user = create_user(email='email@example.net')
        create_deposit(user, amount=500)

        booking_in_35 = create_booking(user, stock=stock_in_35, venue=venue_in_35)
        booking_in_78 = create_booking(user, stock=stock_in_78, venue=venue_in_78)

        payment1 = create_payment(booking_in_35, offerer, amount=20)
        payment2 = create_payment(booking_in_78, offerer, amount=10)

        PcObject.save(user, venue_in_78, venue_in_35, payment1, payment2)

        # When
        total_amount_to_pay = get_total_amount_to_pay('35')

        # Then
        assert total_amount_to_pay == 20


class QueryGetTop20OffersByNumberOfBookingsTest:
    @clean_database
    def test_returns_20_most_booked_offers_ordered_by_quantity_booked(self, app):
        # Given
        quantities = [14, 15, 16, 17, 18, 19, 20, 21, 22, 22, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        bookings = _create_bookings_with_quantities(quantities)
        PcObject.save(*bookings)
        expected_counts = [
            ('8', 22, 0), ('9', 22, 0), ('7', 21, 0), ('6', 20, 0), ('5', 19, 0), ('4', 18, 0),
            ('3', 17, 0), ('2', 16, 0), ('1', 15, 0), ('0', 14, 0), ('23', 14, 0), ('22', 13, 0),
            ('21', 12, 0), ('20', 11, 0), ('19', 10, 0), ('18', 9, 0), ('17', 8, 0), ('16', 7, 0),
            ('15', 6, 0), ('14', 5, 0)
        ]

        # When
        bookings_counts = _query_get_top_20_offers_by_number_of_bookings()

        # Then
        assert bookings_counts == expected_counts

    @clean_database
    def test_does_not_count_cancelled_bookings(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        user = create_user()
        booking = create_booking(user, stock, quantity=1, is_cancelled=True)
        PcObject.save(booking)

        # When
        bookings_counts = _query_get_top_20_offers_by_number_of_bookings()

        # Then
        assert bookings_counts == []

    @clean_database
    def test_amount_is_sum_of_quantity_times_product_of_non_cancelled_bookings(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, thing_name='Offer Name')
        stock1 = create_stock(offer=offer, price=10)
        stock2 = create_stock(offer=offer, price=20)
        user = create_user()
        create_deposit(user, amount=500)
        booking1 = create_booking(user, stock1, quantity=1, is_cancelled=False)
        booking2 = create_booking(user, stock2, quantity=2, is_cancelled=False)
        booking3 = create_booking(user, stock2, quantity=1, is_cancelled=True)
        PcObject.save(booking1, booking2, booking3)

        # When
        bookings_counts = _query_get_top_20_offers_by_number_of_bookings()

        # Then
        assert bookings_counts == [('Offer Name', 3, 50)]

    @clean_database
    def test_returns_offers_filterd_by_departement(self, app):
        # Given
        offerer = create_offerer(siren='111111111')
        venue_in_78 = create_venue(offerer, postal_code='78490', siret='11111111100002')
        venue_in_35 = create_venue(offerer, postal_code='35238', siret='11111111100001')
        offer_in_78 = create_offer_with_thing_product(venue_in_78, thing_name='First offer')
        offer_in_35 = create_offer_with_thing_product(venue_in_35, thing_name='Second offer')
        stock1 = create_stock(offer=offer_in_78, price=10)
        stock2 = create_stock(offer=offer_in_35, price=20)
        user = create_user()
        create_deposit(user, amount=500)
        booking1 = create_booking(user, stock1, quantity=1)
        booking2 = create_booking(user, stock2, quantity=2)
        booking3 = create_booking(user, stock2, quantity=1)
        PcObject.save(booking1, booking2, booking3, venue_in_35, venue_in_78)

        # When
        bookings_counts = _query_get_top_20_offers_by_number_of_bookings('35')

        # Then
        assert bookings_counts == [('Second offer', 3, 60)]


class GetTop20OffersByNumberOfBookingsTest:
    @clean_database
    def test_returns_20_most_booked_offers_ordered_by_quantity_booked_in_data_frame(self, app):
        # Given
        quantities = [14, 15, 16, 17, 18, 19, 20, 21, 22, 22, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        bookings = _create_bookings_with_quantities(quantities)
        PcObject.save(*bookings)
        expected_counts = [
            ('8', 22, 0), ('9', 22, 0), ('7', 21, 0), ('6', 20, 0), ('5', 19, 0), ('4', 18, 0),
            ('3', 17, 0), ('2', 16, 0), ('1', 15, 0), ('0', 14, 0), ('23', 14, 0), ('22', 13, 0),
            ('21', 12, 0), ('20', 11, 0), ('19', 10, 0), ('18', 9, 0), ('17', 8, 0), ('16', 7, 0),
            ('15', 6, 0), ('14', 5, 0)
        ]
        expected_table = pandas.DataFrame(columns=['Offre', 'Nombre de réservations', 'Montant dépensé'],
                                          data=expected_counts)

        # When
        bookings_counts = get_top_20_offers_table()

        # Then
        assert bookings_counts.eq(expected_table).all().all()

    @clean_database
    def test_returns_20_most_booked_offers_ordered_by_quantity_booked_in_data_frame(self, app):
        # Given
        quantities = [14, 15, 16, 17, 18, 19, 20, 21, 22, 22, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        bookings = _create_bookings_with_quantities(quantities)
        PcObject.save(*bookings)
        expected_counts = [
            ('8', 22, 0), ('9', 22, 0), ('7', 21, 0), ('6', 20, 0), ('5', 19, 0), ('4', 18, 0),
            ('3', 17, 0), ('2', 16, 0), ('1', 15, 0), ('0', 14, 0), ('23', 14, 0), ('22', 13, 0),
            ('21', 12, 0), ('20', 11, 0), ('19', 10, 0), ('18', 9, 0), ('17', 8, 0), ('16', 7, 0),
            ('15', 6, 0), ('14', 5, 0)
        ]
        expected_table = pandas.DataFrame(columns=['Offre', 'Nombre de réservations', 'Montant dépensé'],
                                          data=expected_counts)

        # When
        bookings_counts = get_top_20_offers_table()

        # Then
        assert bookings_counts.eq(expected_table).all().all()


class QueryGetTop20OfferersByNumberOfBookingsTest:
    @clean_database
    def test_returns_20_most_booked_offers_ordered_by_quantity_booked(self, app):
        # Given
        quantities = [14, 15, 16, 17, 18, 19, 20, 21, 22, 22, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        bookings = _create_bookings_with_quantities(quantities)
        PcObject.save(*bookings)
        expected_counts = [
            ('Offerer 8', 22, 0), ('Offerer 9', 22, 0), ('Offerer 7', 21, 0), ('Offerer 6', 20, 0),
            ('Offerer 5', 19, 0), ('Offerer 4', 18, 0), ('Offerer 3', 17, 0), ('Offerer 2', 16, 0),
            ('Offerer 1', 15, 0), ('Offerer 0', 14, 0), ('Offerer 23', 14, 0), ('Offerer 22', 13, 0),
            ('Offerer 21', 12, 0), ('Offerer 20', 11, 0), ('Offerer 19', 10, 0), ('Offerer 18', 9, 0),
            ('Offerer 17', 8, 0), ('Offerer 16', 7, 0), ('Offerer 15', 6, 0), ('Offerer 14', 5, 0)
        ]

        # When
        bookings_counts = _query_get_top_20_offerers_by_number_of_bookings()

        # Then
        assert bookings_counts == expected_counts

    @clean_database
    def test_does_not_count_cancelled_bookings(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        user = create_user()
        booking = create_booking(user, stock, quantity=1, is_cancelled=True)
        PcObject.save(booking)

        # When
        bookings_counts = _query_get_top_20_offerers_by_number_of_bookings()

        # Then
        assert bookings_counts == []

    @clean_database
    def test_amount_is_sum_of_quantity_times_product_of_non_cancelled_bookings(self, app):
        # Given
        offerer = create_offerer(name='Offerer Name')
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock1 = create_stock(offer=offer, price=10)
        stock2 = create_stock(offer=offer, price=20)
        user = create_user()
        create_deposit(user, amount=500)
        booking1 = create_booking(user, stock1, quantity=1, is_cancelled=False)
        booking2 = create_booking(user, stock2, quantity=2, is_cancelled=False)
        booking3 = create_booking(user, stock2, quantity=1, is_cancelled=True)
        PcObject.save(booking1, booking2, booking3)

        # When
        bookings_counts = _query_get_top_20_offerers_by_number_of_bookings()

        # Then
        assert bookings_counts == [('Offerer Name', 3, 50)]

    @clean_database
    def test_returns_offerers_filtered_by_departement(self, app):
        # Given
        offerer_in_30 = create_offerer(name='Offerer in 30', siren='111111111')
        offerer_in_57 = create_offerer(name='Offerer in 57', siren='222222222')
        venue_in_30 = create_venue(offerer_in_30, postal_code='30413', siret='11111111100001')
        offer_in_30 = create_offer_with_thing_product(venue=venue_in_30, thing_name='First offer')
        venue_in_57 = create_venue(offerer_in_57, postal_code='57000', siret='22222222200002')
        offer_in_57 = create_offer_with_thing_product(venue=venue_in_57, thing_name='Second offer')
        stock1 = create_stock(offer=offer_in_30, price=31)
        stock2 = create_stock(offer=offer_in_57, price=20)
        user = create_user()
        create_deposit(user, amount=500)
        booking1 = create_booking(user, stock1, quantity=3)
        booking2 = create_booking(user, stock2, quantity=2)
        booking3 = create_booking(user, stock2, quantity=1)
        PcObject.save(offer_in_30, offer_in_57)

        # When
        bookings_counts = _query_get_top_20_offerers_by_number_of_bookings('30')

        # Then
        assert bookings_counts == [('Offerer in 30', 3, 93)]


class GetTop20OfferersByNumberOfBookingsTest:
    @clean_database
    def test_returns_20_most_booked_offers_ordered_by_quantity_booked_in_data_frame(self, app):
        # Given
        quantities = [14, 15, 16, 17, 18, 19, 20, 21, 22, 22, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        bookings = _create_bookings_with_quantities(quantities)
        PcObject.save(*bookings)
        expected_counts = [
            ('Offerer 8', 22, 0), ('Offerer 9', 22, 0), ('Offerer 7', 21, 0), ('Offerer 6', 20, 0),
            ('Offerer 5', 19, 0), ('Offerer 4', 18, 0), ('Offerer 3', 17, 0), ('Offerer 2', 16, 0),
            ('Offerer 1', 15, 0), ('Offerer 0', 14, 0), ('Offerer 23', 14, 0), ('Offerer 22', 13, 0),
            ('Offerer 21', 12, 0), ('Offerer 20', 11, 0), ('Offerer 19', 10, 0), ('Offerer 18', 9, 0),
            ('Offerer 17', 8, 0), ('Offerer 16', 7, 0), ('Offerer 15', 6, 0), ('Offerer 14', 5, 0)
        ]
        expected_table = pandas.DataFrame(columns=['Structure', 'Nombre de réservations', 'Montant dépensé'],
                                          data=expected_counts)

        # When
        bookings_counts = get_top_20_offerers_table_by_number_of_bookings()

        # Then
        assert bookings_counts.eq(expected_table).all().all()


class QueryGetTop20OfferersByAmountTest:
    @clean_database
    def test_does_not_count_cancelled_bookings(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        user = create_user()
        booking = create_booking(user, stock, quantity=1, is_cancelled=True)
        PcObject.save(booking)

        # When
        bookings_counts = _query_get_top_20_offerers_by_booking_amounts()

        # Then
        assert bookings_counts == []

    @clean_database
    def test_returns_20_most_booked_offers_ordered_by_quantity_booked(self, app):
        # Given
        prices = [2, 115, 16, 18, 46, 145, 123, 12, 1, 35, 256, 25, 25, 252, 258, 156, 254, 13, 45, 145, 23]

        bookings = _create_bookings_with_prices(prices)
        PcObject.save(*bookings)
        expected_counts = [
            ('Offerer 14', 1, 258), ('Offerer 10', 1, 256), ('Offerer 16', 1, 254), ('Offerer 13', 1, 252), (
                'Offerer 15', 1, 156), ('Offerer 19', 1, 145), ('Offerer 5', 1, 145), ('Offerer 6', 1, 123), (
                'Offerer 1', 1, 115), ('Offerer 4', 1, 46), ('Offerer 18', 1, 45), ('Offerer 9', 1, 35), (
                'Offerer 11', 1, 25), ('Offerer 12', 1, 25), ('Offerer 20', 1, 23), ('Offerer 3', 1, 18), (
                'Offerer 2', 1, 16), ('Offerer 17', 1, 13), ('Offerer 7', 1, 12), ('Offerer 0', 1, 2)
        ]

        # When
        bookings_counts = _query_get_top_20_offerers_by_booking_amounts()

        # Then
        assert bookings_counts == expected_counts

    @clean_database
    def test_amount_is_sum_of_quantity_times_product_of_non_cancelled_bookings(self, app):
        # Given
        offerer = create_offerer(name='Offerer Name')
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock1 = create_stock(offer=offer, price=10)
        stock2 = create_stock(offer=offer, price=20)
        user = create_user()
        create_deposit(user, amount=500)
        booking1 = create_booking(user, stock1, quantity=1, is_cancelled=False)
        booking2 = create_booking(user, stock2, quantity=2, is_cancelled=False)
        booking3 = create_booking(user, stock2, quantity=1, is_cancelled=True)
        PcObject.save(booking1, booking2, booking3)

        # When
        bookings_counts = _query_get_top_20_offerers_by_booking_amounts()

        # Then
        assert bookings_counts == [('Offerer Name', 3, 50)]

    @clean_database
    def test_returns_offerers_filtered_by_departement_based_on_venue(self, app):
        # Given
        smallshop_only_in_76 = create_offerer(name='Small library', siren='111111111')
        smallshop_venue = create_venue(smallshop_only_in_76, postal_code='76130', siret='11111111100001')
        smallshop_offer = create_offer_with_thing_product(smallshop_venue)
        smallshop_stock_in_76 = create_stock(offer=smallshop_offer, price=30)

        bigstore = create_offerer(name='National book store', siren='222222222')
        bigstore_venue_in_76 = create_venue(bigstore, postal_code='76130', siret='22222222200001')
        bigstore_venue_in_77 = create_venue(bigstore, postal_code='77000', siret='22222222200002')
        bigstore_offer_in_76 = create_offer_with_thing_product(venue=bigstore_venue_in_76)
        bigstore_offer_in_77 = create_offer_with_thing_product(venue=bigstore_venue_in_77)
        bigstore_stock_in_76 = create_stock(offer=bigstore_offer_in_76, price=10)
        bigstore_stock_in_77 = create_stock(offer=bigstore_offer_in_77, price=10)

        user = create_user()
        create_deposit(user, amount=500)
        create_booking(user, smallshop_stock_in_76, quantity=2)
        create_booking(user, bigstore_stock_in_76, quantity=2)
        create_booking(user, bigstore_stock_in_77, quantity=1)

        PcObject.save(smallshop_stock_in_76, bigstore_stock_in_77, bigstore_stock_in_76)

        # When
        bookings_counts = _query_get_top_20_offerers_by_booking_amounts('76')

        # Then
        assert bookings_counts == [('Small library', 2, 60), ('National book store', 2, 20)]


class GetTop20OfferersByAmountTable:
    @clean_database
    def test_returns_20_top_offerers_by_booking_amount_in_a_data_table(self, app):
        # Given
        prices = [2, 115, 16, 18, 46, 145, 123, 12, 1, 35, 256, 25, 25, 252, 258, 156, 254, 13, 45, 145, 23]
        bookings = _create_bookings_with_prices(prices)
        PcObject.save(*bookings)
        expected_counts = [
            ('Offerer 14', 1, 258), ('Offerer 10', 1, 256), ('Offerer 16', 1, 254), ('Offerer 13', 1, 252), (
                'Offerer 15', 1, 156), ('Offerer 19', 1, 145), ('Offerer 5', 1, 145), ('Offerer 6', 1, 123), (
                'Offerer 1', 1, 115), ('Offerer 4', 1, 46), ('Offerer 18', 1, 45), ('Offerer 9', 1, 35), (
                'Offerer 11', 1, 25), ('Offerer 12', 1, 25), ('Offerer 20', 1, 23), ('Offerer 3', 1, 18), (
                'Offerer 2', 1, 16), ('Offerer 17', 1, 13), ('Offerer 7', 1, 12), ('Offerer 0', 1, 2)
        ]
        expected_table = pandas.DataFrame(columns=['Structure', 'Nombre de réservations', 'Montant dépensé'],
                                          data=expected_counts)

        # When
        top_20_offerers_by_amount = get_top_20_offerers_by_amount_table()

        # Then
        assert top_20_offerers_by_amount.eq(expected_table).all().all()


def _create_bookings_with_prices(prices: List[int]):
    siren = 111111111
    bookings = []
    for i, price in enumerate(prices):
        offerer = create_offerer(siren=str(siren), name=f'Offerer {i}')
        venue = create_venue(offerer, siret=offerer.siren + '12345')
        offer = create_offer_with_thing_product(venue, thing_name=f'{i}')
        stock = create_stock(offer=offer, price=price, available=1000)
        user = create_user(email=f'{i}@mail.com')
        deposit = create_deposit(user, amount=500)
        bookings.append(create_booking(user, stock, quantity=1))
        siren += 1
    return bookings


def _create_bookings_with_quantities(quantities: List[int]):
    siren = 111111111
    bookings = []
    for i, quantity in enumerate(quantities):
        offerer = create_offerer(siren=str(siren), name=f'Offerer {i}')
        venue = create_venue(offerer, siret=offerer.siren + '12345')
        offer = create_offer_with_thing_product(venue, thing_name=f'{i}')
        stock = create_stock(offer=offer, price=0, available=1000)
        user = create_user(email=f'{i}@mail.com')
        bookings.append(create_booking(user, stock, quantity=quantity))
        siren += 1
    return bookings
