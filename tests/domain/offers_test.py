from datetime import datetime
from unittest.mock import Mock

from domain.offers import add_stock_alert_message_to_offer
from models import Offer
from models import PcObject
from tests.conftest import clean_database
from tests.test_utils import create_booking, \
    create_deposit, \
    create_offer_with_event_product, \
    create_offer_with_thing_product, \
    create_offerer, \
    create_recommendation, \
    create_user, \
    create_stock_from_offer, \
    create_venue

find_thing = Mock()

offer = Offer()


class AddStockAlertMessageToOfferTest:
    class ThingOfferTest:
        @clean_database
        def test_check_offer_with_no_stock(self, app):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)

            PcObject.save(user, offer)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'pas encore de stock'

        @clean_database
        def test_check_offer_with_all_stocks_unlimited(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=None)
            stock2 = create_stock_from_offer(offer, available=None)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock, venue, recommendation, quantity=3)

            PcObject.save(booking, deposit, user, offer, stock, stock2, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'illimité'

        @clean_database
        def test_check_offer_with_one_unlimited_and_one_available_zero_stock(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=None)
            stock2 = create_stock_from_offer(offer, available=0)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock, venue, recommendation, quantity=3)

            PcObject.save(booking, deposit, user, offer, stock, stock2, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'plus de stock pour 1 offre'

        @clean_database
        def test_check_offer_with_one_available_zero_and_one_sold_out_stock(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=3)
            stock2 = create_stock_from_offer(offer, available=0)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock, venue, recommendation, quantity=3)

            PcObject.save(booking, deposit, user, offer, stock, stock2, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'plus de stock'

        @clean_database
        def test_check_offer_with_all_sold_out_stocks(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=3)
            stock2 = create_stock_from_offer(offer, available=10)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock, venue, recommendation, quantity=3)
            booking2 = create_booking(user2, stock2, venue, recommendation, quantity=10)

            PcObject.save(booking, booking2, deposit, user, offer, stock, stock2, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'plus de stock'

        @clean_database
        def test_check_offer_with_all_remaining_stocks(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=10)
            stock2 = create_stock_from_offer(offer, available=150)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock, venue, recommendation, quantity=3)
            booking2 = create_booking(user2, stock2, venue, recommendation, quantity=20)

            PcObject.save(booking, booking2, deposit, user, offer, stock, stock2, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'encore 137 en stock'

        @clean_database
        def test_check_offer_with_one_sold_out_and_one_remaining_stock(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=8)
            stock2 = create_stock_from_offer(offer, available=10)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock2, venue, recommendation, quantity=10)

            PcObject.save(booking, deposit, user, offer, stock, stock2, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'plus de stock pour 1 offre'

        @clean_database
        def test_check_offer_with_two_sold_out_one_unlimited_and_one_remaining_stocks(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            recommendation = create_recommendation(offer, user)

            stock = create_stock_from_offer(offer, available=10)
            stock2 = create_stock_from_offer(offer, available=5)
            stock3 = create_stock_from_offer(offer, available=1)
            stock4 = create_stock_from_offer(offer, available=None)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock2, venue, recommendation, quantity=5)
            booking2 = create_booking(user2, stock3, venue, recommendation, quantity=1)

            PcObject.save(booking, booking2, deposit, user, offer, stock, stock2, stock3, stock4, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'plus de stock pour 2 offres'


    class EventOfferTest:
        @clean_database
        def test_check_offer_with_no_stock(self, app):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)

            PcObject.save(user, offer)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'pas encore de places'

        @clean_database
        def test_check_offer_with_all_stocks_unlimited(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=None)
            stock2 = create_stock_from_offer(offer, available=None)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock, venue, recommendation, quantity=3)

            PcObject.save(booking, deposit, user, offer, stock, stock2, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'illimité'


        @clean_database
        def test_check_offer_with_one_unlimited_and_one_available_zero_stock(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=None)
            stock2 = create_stock_from_offer(offer, available=0)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock, venue, recommendation, quantity=3)

            PcObject.save(booking, deposit, user, offer, stock, stock2, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'plus de places pour 1 offre'


        @clean_database
        def test_check_offer_with_one_available_zero_and_one_sold_out_stock(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=3)
            stock2 = create_stock_from_offer(offer, available=0)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock, venue, recommendation, quantity=3)

            PcObject.save(booking, deposit, user, offer, stock, stock2, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'plus de places pour toutes les dates'


        @clean_database
        def test_check_offer_with_all_sold_out_stocks(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=3)
            stock2 = create_stock_from_offer(offer, available=10)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock, venue, recommendation, quantity=3)
            booking2 = create_booking(user2, stock2, venue, recommendation, quantity=10)

            PcObject.save(booking, booking2, deposit, user, offer, stock, stock2, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'plus de places pour toutes les dates'

        @clean_database
        def test_check_offer_with_all_remaining_stocks(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=10)
            stock2 = create_stock_from_offer(offer, available=40)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock, venue, recommendation, quantity=3)
            booking2 = create_booking(user2, stock2, venue, recommendation, quantity=11)

            PcObject.save(booking, booking2, deposit, user, offer, stock, stock2, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'encore 36 places'

        @clean_database
        def test_check_offer_with_one_sold_out_and_one_remaining_stock(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=8)
            stock2 = create_stock_from_offer(offer, available=10)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock2, venue, recommendation, quantity=10)

            PcObject.save(booking, deposit, user, offer, stock, stock2, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'plus de places pour 1 offre'

        @clean_database
        def test_check_offer_with_two_sold_out_one_unlimited_and_one_remaining_stocks(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            recommendation = create_recommendation(offer, user)

            stock = create_stock_from_offer(offer, available=10)
            stock2 = create_stock_from_offer(offer, available=5)
            stock3 = create_stock_from_offer(offer, available=1)
            stock4 = create_stock_from_offer(offer, available=None)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock2, venue, recommendation, quantity=5)
            booking2 = create_booking(user2, stock3, venue, recommendation, quantity=1)

            PcObject.save(booking, booking2, deposit, user, offer, stock, stock2, stock3, stock4, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'plus de places pour 2 offres'
