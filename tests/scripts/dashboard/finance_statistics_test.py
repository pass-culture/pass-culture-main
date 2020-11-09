from typing import List

import pandas
import pytest

from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_deposit
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_payment
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import EventType
from pcapi.models import ThingType
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository import repository
from pcapi.scripts.dashboard.finance_statistics import _query_get_top_20_offerers_by_booking_amounts
from pcapi.scripts.dashboard.finance_statistics import _query_get_top_20_offerers_by_number_of_bookings
from pcapi.scripts.dashboard.finance_statistics import _query_get_top_20_offers_by_number_of_bookings
from pcapi.scripts.dashboard.finance_statistics import get_top_20_offerers_by_amount_table
from pcapi.scripts.dashboard.finance_statistics import get_top_20_offerers_table_by_number_of_bookings
from pcapi.scripts.dashboard.finance_statistics import get_top_20_offers_table
from pcapi.scripts.dashboard.finance_statistics import get_total_amount_spent
from pcapi.scripts.dashboard.finance_statistics import get_total_amount_to_pay
from pcapi.scripts.dashboard.finance_statistics import get_total_deposits

from tests.conftest import clean_database


class GetTotalDepositsTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_0_if_no_deposits(self, app):
        # When
        total_deposits = get_total_deposits()

        # Then
        assert total_deposits == 0

    @pytest.mark.usefixtures("db_session")
    def test_returns_1000_if_two_deposits(self, app):
        # Given
        user1 = create_user(email='test1@email.com')
        deposit1 = create_deposit(user1, amount=500)
        user2 = create_user(email='test2@email.com')
        deposit2 = create_deposit(user2, amount=500)

        repository.save(deposit1, deposit2)

        # When
        total_deposits = get_total_deposits()

        # Then
        assert total_deposits == 1000

    @pytest.mark.usefixtures("db_session")
    def test_returns_500_if_two_deposits_but_filtered_by_departement(self, app):
        # Given
        user1 = create_user(departement_code='42', email='test1@email.com')
        deposit1 = create_deposit(user1, amount=500)
        user2 = create_user(departement_code='95', email='test2@email.com')
        deposit2 = create_deposit(user2, amount=500)

        repository.save(deposit1, deposit2)

        # When
        total_deposits = get_total_deposits('95')

        # Then
        assert total_deposits == 500


class GetTotalAmountSpentTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_0_if_no_bookings(self, app):
        # When
        total_amount_spent = get_total_amount_spent()

        # Then
        assert total_amount_spent == 0

    @pytest.mark.usefixtures("db_session")
    def test_returns_20_if_two_booking_with_amount_10(self, app):
        # Given
        user1 = create_user(email='email1@test.com')
        user2 = create_user(email='email2@test.com')
        deposit1 = create_deposit(user1, amount=500)
        deposit2 = create_deposit(user2, amount=500)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=10)
        booking1 = create_booking(user=user1, stock=stock, venue=venue)
        booking2 = create_booking(user=user2, stock=stock, venue=venue)
        repository.save(booking1, booking2, deposit1, deposit2)

        # When
        total_amount_spent = get_total_amount_spent()

        # Then
        assert total_amount_spent == 20

    @pytest.mark.usefixtures("db_session")
    def test_returns_10_if_two_booking_with_amount_10_and_one_cancelled(self, app):
        # Given
        user1 = create_user(email='email1@test.com')
        user2 = create_user(email='email2@test.com')
        deposit1 = create_deposit(user1, amount=500)
        deposit2 = create_deposit(user2, amount=500)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=10)
        booking1 = create_booking(user=user1, stock=stock, venue=venue)
        booking2 = create_booking(user=user2, stock=stock, is_cancelled=True, venue=venue)
        repository.save(booking1, booking2, deposit1, deposit2)

        # When
        total_amount_spent = get_total_amount_spent()

        # Then
        assert total_amount_spent == 10

    @pytest.mark.usefixtures("db_session")
    def test_returns_20_if_one_booking_with_amount_10_and_quantity_2(self, app):
        # Given
        user = create_user(email='email1@test.com')
        deposit = create_deposit(user, amount=500)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=10)
        booking = create_booking(user=user, stock=stock, quantity=2, venue=venue)
        repository.save(booking, deposit)

        # When
        total_amount_spent = get_total_amount_spent()

        # Then
        assert total_amount_spent == 20

    @pytest.mark.usefixtures("db_session")
    def test_returns_15_if_two_bookings_but_only_one_the_filtered_departement(self, app):
        # Given
        user67 = create_user(departement_code='67', email='email67@test.com')
        create_deposit(user67, amount=500)
        user89 = create_user(departement_code='89', email='email89@test.com')
        create_deposit(user89, amount=500)

        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=15)
        booking_in_67 = create_booking(user=user67, stock=stock, venue=venue)
        booking_in_89 = create_booking(user=user89, stock=stock, venue=venue)
        repository.save(booking_in_67, booking_in_89, user67, user89)

        # When
        total_amount_spent = get_total_amount_spent('67')

        # Then
        assert total_amount_spent == 15


class GetTotalAmountToPayTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_0_if_no_payments(self, app):
        # When
        total_amount_to_pay = get_total_amount_to_pay()

        # Then
        assert total_amount_to_pay == 0

    @pytest.mark.usefixtures("db_session")
    def test_returns_20_if_one_payment_with_amount_10_and_one_with_amount_5(self, app):
        # Given
        user1 = create_user(email='email1@test.com')
        user2 = create_user(email='email2@test.com')
        deposit1 = create_deposit(user1, amount=500)
        deposit2 = create_deposit(user2, amount=500)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=10)
        booking1 = create_booking(user=user1, stock=stock, venue=venue)
        booking2 = create_booking(user=user2, stock=stock, venue=venue)
        payment1 = create_payment(booking1, offerer, amount=5)
        payment2 = create_payment(booking2, offerer, amount=10)
        repository.save(payment1, payment2)

        # When
        total_amount_to_pay = get_total_amount_to_pay()

        # Then
        assert total_amount_to_pay == 15

    @pytest.mark.usefixtures("db_session")
    def test_returns_0_if_last_payment_status_banned(self, app):
        # Given
        user = create_user(email='email@test.com')
        deposit = create_deposit(user, amount=500)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=10)
        booking = create_booking(user=user, stock=stock, venue=venue)
        payment = create_payment(booking, offerer, amount=5, status=TransactionStatus.BANNED)
        repository.save(payment)

        # When
        total_amount_to_pay = get_total_amount_to_pay()

        # Then
        assert total_amount_to_pay == 0

    @pytest.mark.usefixtures("db_session")
    def test_returns_5_if_amount_5_and_last_payment_status_not_banned(self, app):
        # Given
        user = create_user(email='email@test.com')
        deposit = create_deposit(user, amount=500)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=10)
        booking = create_booking(user=user, stock=stock, venue=venue)
        payment = create_payment(booking, offerer, amount=5, status=TransactionStatus.BANNED)
        payment.setStatus(TransactionStatus.RETRY)
        repository.save(payment)

        # When
        total_amount_to_pay = get_total_amount_to_pay()

        # Then
        assert total_amount_to_pay == 5

    @pytest.mark.usefixtures("db_session")
    def test_returns_only_payment_total_by_department(self, app):
        # Given
        offerer = create_offerer(siren='111111111')
        venue = create_venue(offerer, postal_code='78490', siret='11111111100002')
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=10)

        user_in_35 = create_user(departement_code='35', email='email35@example.net')
        user_in_78 = create_user(departement_code='78', email='email78@example.net')
        create_deposit(user_in_35, amount=500)
        create_deposit(user_in_78, amount=500)

        booking_in_35 = create_booking(user=user_in_35, stock=stock, venue=venue)
        booking_in_78 = create_booking(user=user_in_78, stock=stock, venue=venue)

        payment1 = create_payment(booking_in_35, offerer, amount=20)
        payment2 = create_payment(booking_in_78, offerer, amount=10)

        repository.save(user_in_35, venue, payment1, payment2)

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
        repository.save(*bookings)
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

    @pytest.mark.usefixtures("db_session")
    def test_does_not_count_cancelled_bookings(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        user = create_user()
        booking = create_booking(user=user, stock=stock, is_cancelled=True, quantity=1)
        repository.save(booking)

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
        booking1 = create_booking(user=user, stock=stock1, is_cancelled=False, quantity=1)
        booking2 = create_booking(user=user, stock=stock2, is_cancelled=False, quantity=2)
        booking3 = create_booking(user=user, stock=stock2, is_cancelled=True, quantity=1)
        repository.save(booking1, booking2, booking3)

        # When
        bookings_counts = _query_get_top_20_offers_by_number_of_bookings()

        # Then
        assert bookings_counts == [('Offer Name', 3, 50)]

    @pytest.mark.usefixtures("db_session")
    def test_does_not_return_activation_offers(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        offer2 = create_offer_with_event_product(venue, event_type=EventType.ACTIVATION)
        stock1 = create_stock(offer=offer1, price=10)
        stock2 = create_stock(offer=offer2, price=20)
        user = create_user()
        create_deposit(user, amount=500)
        booking1 = create_booking(user=user, stock=stock1, is_cancelled=False, quantity=1)
        booking2 = create_booking(user=user, stock=stock2, is_cancelled=False, quantity=1)
        repository.save(booking1, booking2)

        # When
        bookings_counts = _query_get_top_20_offers_by_number_of_bookings()

        # Then
        assert bookings_counts == []

    @clean_database
    def test_returns_offers_filterd_by_departement(self, app):
        # Given
        offerer = create_offerer(siren='111111111')
        venue = create_venue(offerer, postal_code='78490', siret='11111111100002')
        offer = create_offer_with_thing_product(venue, thing_name='Offer')
        stock = create_stock(offer=offer, price=10)
        user_in_78 = create_user(departement_code='78', email='user78@email.com')
        user_in_35 = create_user(departement_code='35', email='user35@email.com')
        create_deposit(user_in_78, amount=500)
        create_deposit(user_in_35, amount=500)
        booking1 = create_booking(user=user_in_78, stock=stock, quantity=1)
        booking2 = create_booking(user=user_in_35, stock=stock, quantity=2)
        repository.save(booking1, booking2)

        # When
        bookings_counts = _query_get_top_20_offers_by_number_of_bookings('35')

        # Then
        assert bookings_counts == [('Offer', 2, 20)]

    @pytest.mark.usefixtures("db_session")
    def test_returns_does_not_return_activation_offers_filterd_by_departement(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code='35000')
        offer1 = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        offer2 = create_offer_with_event_product(venue, event_type=EventType.ACTIVATION)
        stock1 = create_stock(offer=offer1, price=10)
        stock2 = create_stock(offer=offer2, price=20)
        user = create_user()
        create_deposit(user, amount=500)
        booking1 = create_booking(user=user, stock=stock1, is_cancelled=False, quantity=1)
        booking2 = create_booking(user=user, stock=stock2, is_cancelled=False, quantity=1)
        repository.save(booking1, booking2)

        # When
        bookings_counts = _query_get_top_20_offers_by_number_of_bookings('35')

        # Then
        assert bookings_counts == []


class GetTop20OffersByNumberOfBookingsTest:
    @clean_database
    def test_returns_20_most_booked_offers_ordered_by_quantity_booked_in_data_frame(self, app):
        # Given
        quantities = [14, 15, 16, 17, 18, 19, 20, 21, 22, 22, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        bookings = _create_bookings_with_quantities(quantities)
        repository.save(*bookings)
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
        repository.save(*bookings)
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

    @pytest.mark.usefixtures("db_session")
    def test_does_not_count_cancelled_bookings(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        user = create_user()
        booking = create_booking(user=user, stock=stock, is_cancelled=True, quantity=1)
        repository.save(booking)

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
        booking1 = create_booking(user=user, stock=stock1, is_cancelled=False, quantity=1)
        booking2 = create_booking(user=user, stock=stock2, is_cancelled=False, quantity=2)
        booking3 = create_booking(user=user, stock=stock2, is_cancelled=True, quantity=1)
        repository.save(booking1, booking2, booking3)

        # When
        bookings_counts = _query_get_top_20_offerers_by_number_of_bookings()

        # Then
        assert bookings_counts == [('Offerer Name', 3, 50)]

    @clean_database
    def test_returns_offerers_filtered_by_departement(self, app):
        # Given
        offerer = create_offerer(name='Offerer', siren='111111111')
        venue = create_venue(offerer, postal_code='76413', siret='11111111100001')
        offer = create_offer_with_thing_product(venue=venue, thing_name='Offer')
        stock = create_stock(offer=offer, price=31)
        user_30 = create_user(departement_code=30)
        user_57 = create_user(departement_code='57', email='t@est.com')
        create_deposit(user_30, amount=500)
        create_deposit(user_57, amount=500)
        booking1 = create_booking(user=user_30, stock=stock, quantity=3)
        booking2 = create_booking(user=user_57, stock=stock, quantity=2)
        repository.save(booking1, booking2)

        # When
        bookings_counts = _query_get_top_20_offerers_by_number_of_bookings('30')

        # Then
        assert bookings_counts == [('Offerer', 3, 93)]

    @pytest.mark.usefixtures("db_session")
    def test_does_not_return_offerers_with_only_activation_offers(self, app):
        # Given
        offerer = create_offerer(name='Offerer Name')
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        offer2 = create_offer_with_event_product(venue, event_type=EventType.ACTIVATION)
        stock1 = create_stock(offer=offer1, price=10)
        stock2 = create_stock(offer=offer2, price=20)
        user = create_user()
        create_deposit(user, amount=500)
        booking1 = create_booking(user=user, stock=stock1, is_cancelled=False, quantity=1)
        booking2 = create_booking(user=user, stock=stock2, is_cancelled=False, quantity=2)
        repository.save(booking1, booking2)

        # When
        bookings_counts = _query_get_top_20_offerers_by_number_of_bookings()

        # Then
        assert bookings_counts == []

    @pytest.mark.usefixtures("db_session")
    def test_does_not_return_offerers_with_only_activation_offers_filtered_by_departement(self, app):
        # Given
        offerer = create_offerer(name='Offerer Name')
        venue = create_venue(offerer, postal_code='75290')
        offer1 = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        offer2 = create_offer_with_event_product(venue, event_type=EventType.ACTIVATION)
        stock1 = create_stock(offer=offer1, price=10)
        stock2 = create_stock(offer=offer2, price=20)
        user = create_user(departement_code='76')
        create_deposit(user, amount=500)
        booking1 = create_booking(user=user, stock=stock1, is_cancelled=False, quantity=1)
        booking2 = create_booking(user=user, stock=stock2, is_cancelled=False, quantity=2)
        repository.save(booking1, booking2)

        # When
        bookings_counts = _query_get_top_20_offerers_by_number_of_bookings('76')

        # Then
        assert bookings_counts == []


class GetTop20OfferersByNumberOfBookingsTest:
    @clean_database
    def test_returns_20_most_booked_offers_ordered_by_quantity_booked_in_data_frame(self, app):
        # Given
        quantities = [14, 15, 16, 17, 18, 19, 20, 21, 22, 22, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        bookings = _create_bookings_with_quantities(quantities)
        repository.save(*bookings)
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
    @pytest.mark.usefixtures("db_session")
    def test_does_not_count_cancelled_bookings(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        user = create_user()
        booking = create_booking(user=user, stock=stock, is_cancelled=True, quantity=1)
        repository.save(booking)

        # When
        bookings_counts = _query_get_top_20_offerers_by_booking_amounts()

        # Then
        assert bookings_counts == []

    @clean_database
    def test_returns_20_most_booked_offers_ordered_by_quantity_booked(self, app):
        # Given
        prices = [2, 115, 16, 18, 46, 145, 123, 12, 1, 35, 256, 25, 25, 252, 258, 156, 254, 13, 45, 145, 23]

        bookings = _create_bookings_with_prices(prices)
        repository.save(*bookings)
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
        booking1 = create_booking(user=user, stock=stock1, is_cancelled=False, quantity=1)
        booking2 = create_booking(user=user, stock=stock2, is_cancelled=False, quantity=2)
        booking3 = create_booking(user=user, stock=stock2, is_cancelled=True, quantity=1)
        repository.save(booking1, booking2, booking3)

        # When
        bookings_counts = _query_get_top_20_offerers_by_booking_amounts()

        # Then
        assert bookings_counts == [('Offerer Name', 3, 50)]

    @clean_database
    def test_returns_offerers_filtered_by_departement_based_on_venue(self, app):
        # Given
        offerer1 = create_offerer(name='Small library', siren='111111111')
        venue1 = create_venue(offerer1, postal_code='33130', siret='11111111100001')
        offer1 = create_offer_with_thing_product(venue1)
        stock1 = create_stock(offer=offer1, price=30)

        offerer2 = create_offerer(name='National book store', siren='222222222')
        venue2 = create_venue(offerer2, postal_code='33130', siret='22222222200001')
        offer2 = create_offer_with_thing_product(venue=venue2)
        stock2 = create_stock(offer=offer2, price=10)

        user_76 = create_user(departement_code='76')
        user_77 = create_user(departement_code='77', email='e@mail.com')
        create_deposit(user_76, amount=500)
        create_deposit(user_77, amount=500)
        booking1 = create_booking(user=user_76, stock=stock1, quantity=2)
        booking2 = create_booking(user=user_76, stock=stock2, quantity=2)
        booking3 = create_booking(user=user_77, stock=stock2, quantity=2)

        repository.save(booking1, booking2, booking3)

        # When
        bookings_counts = _query_get_top_20_offerers_by_booking_amounts('76')

        # Then
        assert bookings_counts == [('Small library', 2, 60), ('National book store', 2, 20)]

    @pytest.mark.usefixtures("db_session")
    def test_does_not_return_offerers_with_only_activation_offer(self, app):
        # Given
        offerer = create_offerer(name='Offerer Name')
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        offer2 = create_offer_with_event_product(venue, event_type=EventType.ACTIVATION)
        stock1 = create_stock(offer=offer1, price=10)
        stock2 = create_stock(offer=offer2, price=20)
        user = create_user()
        create_deposit(user, amount=500)
        booking1 = create_booking(user=user, stock=stock1, is_cancelled=False, quantity=1)
        booking2 = create_booking(user=user, stock=stock2, is_cancelled=False, quantity=2)
        repository.save(booking1, booking2)

        # When
        bookings_counts = _query_get_top_20_offerers_by_booking_amounts()

        # Then
        assert bookings_counts == []

    @pytest.mark.usefixtures("db_session")
    def test_does_not_return_offerers_with_only_activation_offer_filtered_by_departement(self, app):
        # Given
        offerer = create_offerer(name='Offerer Name')
        venue = create_venue(offerer, postal_code='34790')
        offer1 = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        offer2 = create_offer_with_event_product(venue, event_type=EventType.ACTIVATION)
        stock1 = create_stock(offer=offer1, price=10)
        stock2 = create_stock(offer=offer2, price=20)
        user = create_user(departement_code='34')
        create_deposit(user, amount=500)
        booking1 = create_booking(user=user, stock=stock1, is_cancelled=False, quantity=1)
        booking2 = create_booking(user=user, stock=stock2, is_cancelled=False, quantity=2)
        repository.save(booking1, booking2)

        # When
        bookings_counts = _query_get_top_20_offerers_by_booking_amounts('34')

        # Then
        assert bookings_counts == []


class GetTop20OfferersByAmountTable:
    @clean_database
    def test_returns_20_top_offerers_by_booking_amount_in_a_data_table(self, app):
        # Given
        prices = [2, 115, 16, 18, 46, 145, 123, 12, 1, 35, 256, 25, 25, 252, 258, 156, 254, 13, 45, 145, 23]
        bookings = _create_bookings_with_prices(prices)
        repository.save(*bookings)
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
        stock = create_stock(offer=offer, price=price, quantity=1000)
        user = create_user(email=f'{i}@mail.com')
        deposit = create_deposit(user, amount=500)
        bookings.append(create_booking(user=user, stock=stock, quantity=1))
        siren += 1
    return bookings


def _create_bookings_with_quantities(quantities: List[int]):
    siren = 111111111
    bookings = []
    for i, quantity in enumerate(quantities):
        offerer = create_offerer(siren=str(siren), name=f'Offerer {i}')
        venue = create_venue(offerer, siret=offerer.siren + '12345')
        offer = create_offer_with_thing_product(venue, thing_name=f'{i}')
        stock = create_stock(offer=offer, price=0, quantity=1000)
        user = create_user(email=f'{i}@mail.com')
        bookings.append(create_booking(user=user, stock=stock, quantity=quantity))
        siren += 1
    return bookings
