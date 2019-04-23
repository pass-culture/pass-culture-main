from unittest.mock import Mock

import pytest

from models import PcObject
from domain.offers import add_stock_alert_message_to_offer, check_digital_offer_consistency, InconsistentOffer
from models import Offer, Venue, Thing
from datetime import datetime
from tests.test_utils import API_URL, \
    create_booking, \
    create_deposit, \
    create_event_offer, \
    create_event_offer, \
    create_offerer, \
    create_recommendation, \
    create_user, \
    create_user_offerer, \
    create_stock_from_offer, \
    create_venue, create_thing_offer, create_bank_information

from tests.conftest import clean_database

find_thing = Mock()

offer = Offer()
offer.thingId = 20


@pytest.mark.standalone
class CheckDigitalOfferConsistencyTest:
    def test_raises_an_error_for_physical_venue_and_digital_thing(self):
        # given
        venue = Venue(from_dict={'isVirtual': False})
        find_thing.return_value = Thing(from_dict={'url': 'https://zerlngzergner.fr'})

        # when
        with pytest.raises(InconsistentOffer) as e:
            check_digital_offer_consistency(offer, venue, find_thing=find_thing)

        # then
        assert str(e.value) == 'Offer.venue is not virtual but Offer.thing has an URL'

    def test_does_not_raise_an_error_for_virtual_venue_and_digital_thing(self):
        # given
        venue = Venue(from_dict={'isVirtual': True})
        find_thing.return_value = Thing(from_dict={'url': 'https://zerlngzergner.fr'})

        # when
        result = check_digital_offer_consistency(offer, venue, find_thing=find_thing)

        # then
        assert result is None

    def test_raises_an_error_for_virtual_venue_and_physical_thing(self):
        # given
        venue = Venue(from_dict={'isVirtual': True})
        find_thing.return_value = Thing(from_dict={'url': None})

        # when
        with pytest.raises(InconsistentOffer) as e:
            check_digital_offer_consistency(offer, venue, find_thing=find_thing)

        # then
        assert str(e.value) == 'Offer.venue is virtual but Offer.thing does not have an URL'

    def test_does_not_raise_an_error_for_physical_venue_and_physical_thing(self):
        # given
        venue = Venue(from_dict={'isVirtual': False})
        find_thing.return_value = Thing(from_dict={'url': None})

        # when
        result = check_digital_offer_consistency(offer, venue, find_thing=find_thing)

        # then
        assert result is None

@pytest.mark.standalone
class AddStockAlertMessageToOfferTest:
    class ThingOfferTest:
        @clean_database
        def test_check_alert_stock_message_returned_with_empty_stock(self, app):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_thing_offer(venue)

            PcObject.check_and_save(user, offer)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'pas encore de stock'

        @clean_database
        def test_check_alert_stock_message_returned_all_stock_unlimited(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_thing_offer(venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=None)
            stock2 = create_stock_from_offer(offer, available=None)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock, venue, recommendation, quantity=3)

            PcObject.check_and_save(booking, deposit, user, offer, stock, stock2, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'illimité'

        @clean_database
        def test_check_alert_stock_message_returned_all_stock_unlimited_and_available_set_to_zero(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_thing_offer(venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=None)
            stock2 = create_stock_from_offer(offer, available=0)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock, venue, recommendation, quantity=3)

            PcObject.check_and_save(booking, deposit, user, offer, stock, stock2, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'plus de stock pour 1 offre'

        @clean_database
        def test_check_alert_stock_message_returned_all_empty_stock_after_booking_and_one_with_available_set_to_zero(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_thing_offer(venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=3)
            stock2 = create_stock_from_offer(offer, available=0)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock, venue, recommendation, quantity=3)

            PcObject.check_and_save(booking, deposit, user, offer, stock, stock2, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'plus de stock'

        @clean_database
        def test_check_alert_stock_message_returned_all_empty_stock_after_bookings(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_thing_offer(venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=3)
            stock2 = create_stock_from_offer(offer, available=10)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock, venue, recommendation, quantity=3)
            booking2 = create_booking(user2, stock2, venue, recommendation, quantity=10)

            PcObject.check_and_save(booking, booking2, deposit, user, offer, stock, stock2, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'plus de stock'

        @clean_database
        def test_check_alert_stock_message_returned_with_stock(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_thing_offer(venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=10)
            stock2 = create_stock_from_offer(offer, available=150)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock, venue, recommendation, quantity=3)
            booking2 = create_booking(user2, stock2, venue, recommendation, quantity=20)

            PcObject.check_and_save(booking, booking2, deposit, user, offer, stock, stock2, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'encore 137 en stock'

        @clean_database
        def test_check_alert_stock_message_returned_with_at_least_one_with_no_more_stock_on_one_offer(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_thing_offer(venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=8)
            stock2 = create_stock_from_offer(offer, available=10)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock2, venue, recommendation, quantity=10)

            PcObject.check_and_save(booking, deposit, user, offer, stock, stock2, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'plus de stock pour 1 offre'

        @clean_database
        def test_check_alert_stock_message_returned_with_at_least_one_with_no_more_stock_on_two_offers_even_with_one_unlimited_stock_and_one_with_stock(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_thing_offer(venue)
            recommendation = create_recommendation(offer, user)

            stock = create_stock_from_offer(offer, available=10)
            stock2 = create_stock_from_offer(offer, available=5)
            stock3 = create_stock_from_offer(offer, available=1)
            stock4 = create_stock_from_offer(offer, available=None)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock2, venue, recommendation, quantity=5)
            booking2 = create_booking(user2, stock3, venue, recommendation, quantity=1)

            PcObject.check_and_save(booking, booking2, deposit, user, offer, stock, stock2, stock3, stock4, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'plus de stock pour 2 offres'


    class EventOfferTest:
        @clean_database
        def test_check_event_alert_stock_message_returned_with_empty_stock(self, app):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_event_offer(venue)

            PcObject.check_and_save(user, offer)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'pas encore de places'

        @clean_database
        def test_check_event_alert_stock_message_returned_all_stock_unlimited(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_event_offer(venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=None)
            stock2 = create_stock_from_offer(offer, available=None)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock, venue, recommendation, quantity=3)

            PcObject.check_and_save(booking, deposit, user, offer, stock, stock2, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'illimité'

        @clean_database
        def test_check_event_alert_stock_message_returned_with_stock(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_event_offer(venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=10)
            stock2 = create_stock_from_offer(offer, available=40)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock, venue, recommendation, quantity=3)
            booking2 = create_booking(user2, stock2, venue, recommendation, quantity=11)

            PcObject.check_and_save(booking, booking2, deposit, user, offer, stock, stock2, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'encore 36 places'

        @clean_database
        def test_check_event_alert_stock_message_returned_with_at_least_one_with_no_more_stock_on_one_offer(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_event_offer(venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=8)
            stock2 = create_stock_from_offer(offer, available=10)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock2, venue, recommendation, quantity=10)

            PcObject.check_and_save(booking, deposit, user, offer, stock, stock2, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'plus de places pour 1 offre'

        @clean_database
        def test_check_event_alert_stock_message_returned_with_at_least_one_with_no_more_stock_on_two_offers_even_with_one_unlimited_stock_and_one_with_stock(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_event_offer(venue)
            recommendation = create_recommendation(offer, user)

            stock = create_stock_from_offer(offer, available=10)
            stock2 = create_stock_from_offer(offer, available=5)
            stock3 = create_stock_from_offer(offer, available=1)
            stock4 = create_stock_from_offer(offer, available=None)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock2, venue, recommendation, quantity=5)
            booking2 = create_booking(user2, stock3, venue, recommendation, quantity=1)

            PcObject.check_and_save(booking, booking2, deposit, user, offer, stock, stock2, stock3, stock4, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'plus de places pour 2 offres'


        @clean_database
        def test_check_event_alert_stock_message_returned_with_no_more_stock_at_all(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_event_offer(venue)
            recommendation = create_recommendation(offer, user)

            stock2 = create_stock_from_offer(offer, available=5)
            stock3 = create_stock_from_offer(offer, available=15)

            deposit = create_deposit(user2, datetime.utcnow(), amount=500)
            booking = create_booking(user2, stock2, venue, recommendation, quantity=5)
            booking2 = create_booking(user2, stock3, venue, recommendation, quantity=15)

            PcObject.check_and_save(booking, booking2, deposit, user, offer, stock2, stock3, user2)

            # when
            result = add_stock_alert_message_to_offer(offer)

            # then
            assert result.stockAlertMessage == 'plus de places pour toutes les dates'
