from datetime import datetime, timedelta

import pandas

from models import PcObject, EventType, ThingType
from scripts.dashboard.diversification_statistics import get_offerer_count, get_offerer_with_stock_count, \
    get_offerers_with_offer_available_on_discovery_count, get_offerers_with_non_cancelled_bookings_count, \
    get_offers_with_user_offerer_and_stock_count, get_offers_available_on_discovery_count, \
    get_offers_with_non_cancelled_bookings_count, get_all_bookings_count, get_all_used_bookings_count, \
    get_all_cancelled_bookings_count, _query_get_offer_counts_grouped_by_type_and_medium, \
    _get_offers_grouped_by_type_and_medium, \
    _get_counts_grouped_by_type_and_medium, _query_get_booking_counts_grouped_by_type_and_medium
from tests.conftest import clean_database
from tests.test_utils import create_user, create_offerer, create_user_offerer, create_stock, \
    create_offer_with_thing_product, create_venue, create_mediation, create_offer_with_event_product, create_booking


class GetOffererWithStockCountTest:
    def test_return_zero_if_no_offerer(self, app):
        # When
        number_of_offerers = get_offerer_with_stock_count()

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_return_1_if_offerer_with_user_offerer_and_stock(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer)
        PcObject.save(user_offerer, stock)

        # When
        number_of_offerers = get_offerer_with_stock_count()

        # Then
        assert number_of_offerers == 1

    @clean_database
    def test_return_0_if_offerer_without_user_offerer(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer)
        PcObject.save(offerer, stock)

        # When
        number_of_offerers = get_offerer_with_stock_count()

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_return_0_if_offerer_without_stock(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        user_offerer = create_user_offerer(user, offerer)

        PcObject.save(user_offerer)

        # When
        number_of_offerers = get_offerer_with_stock_count()

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_return_1_if_offerer_with_user_offerer_and_two_stock(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock1 = create_stock(offer=offer)
        stock2 = create_stock(offer=offer)
        PcObject.save(user_offerer, stock1, stock2)

        # When
        number_of_offerers = get_offerer_with_stock_count()

        # Then
        assert number_of_offerers == 1

    @clean_database
    def test_return_1_if_offerer_with_2_user_offerers_and_stock(self, app):
        # Given
        user1 = create_user()
        user2 = create_user(email='other@email.com')
        offerer = create_offerer()
        user_offerer1 = create_user_offerer(user1, offerer)
        user_offerer2 = create_user_offerer(user2, offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock1 = create_stock(offer=offer)
        stock2 = create_stock(offer=offer)
        PcObject.save(user_offerer1, user_offerer2, stock1, stock2)

        # When
        number_of_offerers = get_offerer_with_stock_count()

        # Then
        assert number_of_offerers == 1


class GetOfferersWithOfferAvailableOnDiscoveryCountTest:
    @clean_database
    def test_returns_0_if_only_offerer_with_inactive_offer(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, is_active=False)
        mediation = create_mediation(offer)
        stock = create_stock(offer=offer)
        PcObject.save(stock)

        # When
        number_of_offerers = get_offerers_with_offer_available_on_discovery_count()

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_returns_0_if_only_offerer_with_offer_without_stock(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, is_active=True)
        mediation = create_mediation(offer)
        PcObject.save(offer)

        # When
        number_of_offerers = get_offerers_with_offer_available_on_discovery_count()

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_returns_0_if_only_offerer_with_unvalidated_venue(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, validation_token='XDFCGHVJBK')
        offer = create_offer_with_thing_product(venue, is_active=True)
        stock = create_stock(offer=offer)
        mediation = create_mediation(offer)
        PcObject.save(stock)

        # When
        number_of_offerers = get_offerers_with_offer_available_on_discovery_count()

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_returns_0_if_only_offerer_without_mediation(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, validation_token='XDFCGHVJBK')
        offer = create_offer_with_thing_product(venue, is_active=True)
        stock = create_stock(offer=offer)
        PcObject.save(stock)

        # When
        number_of_offerers = get_offerers_with_offer_available_on_discovery_count()

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_returns_0_if_stock_passed(self, app):
        # Given
        yesterday = datetime.utcnow() - timedelta(days=1)
        offerer = create_offerer()
        venue = create_venue(offerer, validation_token='XDFCGHVJBK')
        offer = create_offer_with_event_product(venue, is_active=True)
        stock = create_stock(offer=offer, beginning_datetime=yesterday)
        PcObject.save(stock)

        # When
        number_of_offerers = get_offerers_with_offer_available_on_discovery_count()

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_returns_0_if_offerer_not_active(self, app):
        # Given
        offerer = create_offerer(is_active=False)
        venue = create_venue(offerer, validation_token='XDFCGHVJBK')
        offer = create_offer_with_event_product(venue, is_active=True)
        stock = create_stock(offer=offer)
        PcObject.save(stock)

        # When
        number_of_offerers = get_offerers_with_offer_available_on_discovery_count()

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_returns_0_if_offerer_not_validated(self, app):
        # Given
        offerer = create_offerer(validation_token='XDFCGHVJBKNL')
        venue = create_venue(offerer, validation_token='XDFCGHVJBK')
        offer = create_offer_with_event_product(venue, is_active=True)
        stock = create_stock(offer=offer)
        PcObject.save(stock)

        # When
        number_of_offerers = get_offerers_with_offer_available_on_discovery_count()

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_returns_0_if_only_offerer_with_activation_offer(self, app):
        # Given
        offerer = create_offerer(validation_token='XDFCGHVJBKNL')
        venue = create_venue(offerer, validation_token='XDFCGHVJBK')
        offer = create_offer_with_thing_product(venue, is_active=True, thing_type='ThingType.ACTIVATION')
        stock = create_stock(offer=offer)
        PcObject.save(stock)

        # When
        number_of_offerers = get_offerers_with_offer_available_on_discovery_count()

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_returns_1_if_offerer_with_offer_returned_by_get_active_offers(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, is_active=True)
        stock = create_stock(offer=offer)
        mediation = create_mediation(offer)
        PcObject.save(stock)

        # When
        number_of_offerers = get_offerers_with_offer_available_on_discovery_count()

        # Then
        assert number_of_offerers == 1

    @clean_database
    def test_returns_1_if_offerer_with_2_offers_returned_by_get_active_offers(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue, is_active=True)
        offer2 = create_offer_with_thing_product(venue, is_active=True)
        stock1 = create_stock(offer=offer1)
        stock2 = create_stock(offer=offer2)
        mediation1 = create_mediation(offer1)
        mediation2 = create_mediation(offer2)
        PcObject.save(stock1, stock2, offer2)

        # When
        number_of_offerers = get_offerers_with_offer_available_on_discovery_count()

        # Then
        assert number_of_offerers == 1


class GetOfferersWithNonCancelledBookingsCountTest:
    @clean_database
    def test_returns_0_if_no_bookings(self, app):
        # Given
        offerer = create_offerer()
        PcObject.save(offerer)

        # When
        number_of_offerers = get_offerers_with_non_cancelled_bookings_count()

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_returns_1_if_offerer_with_non_cancelled_booking(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        user = create_user()
        booking = create_booking(user, stock)
        PcObject.save(booking)

        # When
        number_of_offerers = get_offerers_with_non_cancelled_bookings_count()

        # Then
        assert number_of_offerers == 1

    @clean_database
    def test_returns_1_if_offerer_with_2_non_cancelled_bookings(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock1 = create_stock(offer=offer, price=0)
        stock2 = create_stock(offer=offer, price=0)
        user = create_user()
        booking1 = create_booking(user, stock1)
        booking2 = create_booking(user, stock2)
        PcObject.save(booking1, booking2)

        # When
        number_of_offerers = get_offerers_with_non_cancelled_bookings_count()

        # Then
        assert number_of_offerers == 1

    @clean_database
    def test_returns_0_if_offerer_with_cancelled_bookings(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        user = create_user()
        booking = create_booking(user, stock, is_cancelled=True)
        PcObject.save(booking)

        # When
        number_of_offerers = get_offerers_with_non_cancelled_bookings_count()

        # Then
        assert number_of_offerers == 0


class GetOffersWithUserOffererAndStockCountTest:
    @clean_database
    def test_returns_0_if_offer_without_user_offerer(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer)
        PcObject.save(stock)

        # When
        number_of_offers = get_offers_with_user_offerer_and_stock_count()

        # Then
        assert number_of_offers == 0

    @clean_database
    def test_returns_1_if_offer_with_user_offerer_and_stock(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer)
        PcObject.save(stock, user_offerer)

        # When
        number_of_offers = get_offers_with_user_offerer_and_stock_count()

        # Then
        assert number_of_offers == 1

    @clean_database
    def test_returns_0_if_offer_without_stock(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        PcObject.save(user_offerer)

        # When
        number_of_offers = get_offers_with_user_offerer_and_stock_count()

        # Then
        assert number_of_offers == 0

    @clean_database
    def test_returns_1_if_offer_with_2_user_offerer_and_stock(self, app):
        # Given
        offerer = create_offerer()
        user1 = create_user()
        user2 = create_user(email='other@email.com')
        user_offerer1 = create_user_offerer(user1, offerer)
        user_offerer2 = create_user_offerer(user2, offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer)
        PcObject.save(stock, user_offerer1)

        # When
        number_of_offers = get_offers_with_user_offerer_and_stock_count()

        # Then
        assert number_of_offers == 1

    @clean_database
    def test_returns_1_if_offer_with_user_offerer_and_2_stocks(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock1 = create_stock(offer=offer)
        stock2 = create_stock(offer=offer)
        PcObject.save(stock1, stock2, user_offerer)

        # When
        number_of_offers = get_offers_with_user_offerer_and_stock_count()

        # Then
        assert number_of_offers == 1


class GetOffersAvailableOnDiscoveryCountTest:
    @clean_database
    def test_returns_0_if_only_offerer_with_inactive_offer(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, is_active=False)
        mediation = create_mediation(offer)
        stock = create_stock(offer=offer)
        PcObject.save(stock)

        # When
        number_of_offers = get_offers_available_on_discovery_count()

        # Then
        assert number_of_offers == 0

    @clean_database
    def test_returns_0_if_only_offerer_with_offer_without_stock(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, is_active=True)
        mediation = create_mediation(offer)
        PcObject.save(offer)

        # When
        number_of_offers = get_offers_available_on_discovery_count()

        # Then
        assert number_of_offers == 0

    @clean_database
    def test_returns_0_if_only_offerer_with_unvalidated_venue(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, validation_token='XDFCGHVJBK')
        offer = create_offer_with_thing_product(venue, is_active=True)
        stock = create_stock(offer=offer)
        mediation = create_mediation(offer)
        PcObject.save(stock)

        # When
        number_of_offers = get_offers_available_on_discovery_count()

        # Then
        assert number_of_offers == 0

    @clean_database
    def test_returns_1_if_only_offerer_without_mediation(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, is_active=True)
        stock = create_stock(offer=offer)
        PcObject.save(stock)

        # When
        number_of_offers = get_offers_available_on_discovery_count()

        # Then
        assert number_of_offers == 1

    @clean_database
    def test_returns_0_if_stock_passed(self, app):
        # Given
        yesterday = datetime.utcnow() - timedelta(days=1)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue, is_active=True)
        stock = create_stock(offer=offer, beginning_datetime=yesterday)
        PcObject.save(stock)

        # When
        number_of_offers = get_offers_available_on_discovery_count()

        # Then
        assert number_of_offers == 0

    @clean_database
    def test_returns_0_if_offerer_not_active(self, app):
        # Given
        offerer = create_offerer(is_active=False)
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue, is_active=True)
        stock = create_stock(offer=offer)
        PcObject.save(stock)

        # When
        number_of_offers = get_offers_available_on_discovery_count()

        # Then
        assert number_of_offers == 0

    @clean_database
    def test_returns_0_if_offerer_not_validated(self, app):
        # Given
        offerer = create_offerer(validation_token='XDFCGHVJBKNL')
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue, is_active=True)
        stock = create_stock(offer=offer)
        PcObject.save(stock)

        # When
        number_of_offers = get_offers_available_on_discovery_count()

        # Then
        assert number_of_offers == 0

    @clean_database
    def test_returns_0_if_only_offerer_with_activation_offer(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, is_active=True, thing_type=str(ThingType.ACTIVATION))
        stock = create_stock(offer=offer)
        PcObject.save(stock)

        # When
        number_of_offers = get_offers_available_on_discovery_count()

        # Then
        assert number_of_offers == 0

    @clean_database
    def test_returns_1_if_offerer_with_offer_returned_by_get_active_offers(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, is_active=True)
        stock = create_stock(offer=offer)
        mediation = create_mediation(offer)
        PcObject.save(stock)

        # When
        number_of_offers = get_offers_available_on_discovery_count()

        # Then
        assert number_of_offers == 1

    @clean_database
    def test_returns_2_if_2_offers_returned_by_get_active_offers(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue, is_active=True)
        offer2 = create_offer_with_thing_product(venue, is_active=True)
        stock1 = create_stock(offer=offer1)
        stock2 = create_stock(offer=offer2)
        mediation1 = create_mediation(offer1)
        mediation2 = create_mediation(offer2)
        PcObject.save(stock1, stock2)
        print(offer1.id)
        print(offer2.id)

        # When
        number_of_offers = get_offers_available_on_discovery_count()

        # Then
        assert number_of_offers == 2


class GetOffersWithNonCancelledBookingsCountTest:
    @clean_database
    def test_returns_0_if_no_bookings(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        PcObject.save(offer)

        # When
        number_of_offers = get_offers_with_non_cancelled_bookings_count()

        # Then
        assert number_of_offers == 0

    @clean_database
    def test_returns_1_if_offer_with_non_cancelled_booking(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        user = create_user()
        booking = create_booking(user, stock)
        PcObject.save(booking)

        # When
        number_of_offers = get_offers_with_non_cancelled_bookings_count()

        # Then
        assert number_of_offers == 1

    @clean_database
    def test_returns_1_if_offer_with_2_non_cancelled_bookings(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock1 = create_stock(offer=offer, price=0)
        stock2 = create_stock(offer=offer, price=0)
        user = create_user()
        booking1 = create_booking(user, stock1)
        booking2 = create_booking(user, stock2)
        PcObject.save(booking1, booking2)

        # When
        number_of_offers = get_offers_with_non_cancelled_bookings_count()

        # Then
        assert number_of_offers == 1

    @clean_database
    def test_returns_0_if_offerer_with_cancelled_bookings(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        user = create_user()
        booking = create_booking(user, stock, is_cancelled=True)
        PcObject.save(booking)

        # When
        number_of_offerers = get_offers_with_non_cancelled_bookings_count()

        # Then
        assert number_of_offerers == 0


class GetAllBookingsCountTest:
    @clean_database
    def test_returns_0_when_no_bookings(self, app):
        # When
        number_of_bookings = get_all_bookings_count()

        # Then
        assert number_of_bookings == 0

    @clean_database
    def test_returns_2_when_bookings_cancelled_or_not(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        user = create_user()
        booking1 = create_booking(user, stock)
        booking2 = create_booking(user, stock, is_cancelled=True)
        PcObject.save(booking1, booking2)

        # When
        number_of_bookings = get_all_bookings_count()

        # Then
        assert number_of_bookings == 2


class GetAllUsedBookingsCountTest:
    @clean_database
    def test_return_1_if_used_booking(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        user = create_user()
        booking = create_booking(user, stock, is_used=True)
        PcObject.save(booking)

        # When
        number_of_bookings = get_all_used_bookings_count()

        # Then
        assert number_of_bookings == 1

    @clean_database
    def test_return_0_if_thing_booking_not_used(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        thing_offer = create_offer_with_thing_product(venue)
        thing_stock = create_stock(offer=thing_offer, price=0)
        user = create_user()
        thing_booking = create_booking(user, thing_stock, is_used=False)
        PcObject.save(thing_booking)

        # When
        number_of_bookings = get_all_used_bookings_count()

        # Then
        assert number_of_bookings == 0

    @clean_database
    def test_return_1_if_event_booking_started_more_than_48_hours_ago(self, app):
        # Given
        more_than_48_hours_ago = datetime.utcnow() - timedelta(hours=49)
        two_days_ago = datetime.utcnow() - timedelta(hours=48)
        offerer = create_offerer()
        venue = create_venue(offerer)
        event_offer = create_offer_with_event_product(venue)
        event_stock = create_stock(offer=event_offer, price=0, beginning_datetime=more_than_48_hours_ago,
                                   end_datetime=two_days_ago,
                                   booking_limit_datetime=more_than_48_hours_ago - timedelta(hours=1))
        user = create_user()
        event_booking = create_booking(user, event_stock, is_used=False)
        PcObject.save(event_booking)

        # When
        number_of_bookings = get_all_used_bookings_count()

        # Then
        assert number_of_bookings == 1

    @clean_database
    def test_return_0_if_event_booking_started_47_hours_ago(self, app):
        # Given
        less_than_48_hours_ago = datetime.utcnow() - timedelta(hours=47)
        offerer = create_offerer()
        venue = create_venue(offerer)
        event_offer = create_offer_with_event_product(venue)
        event_stock = create_stock(
            offer=event_offer,
            price=0,
            beginning_datetime=less_than_48_hours_ago,
            end_datetime=less_than_48_hours_ago + timedelta(hours=1),
            booking_limit_datetime=less_than_48_hours_ago - timedelta(hours=1)
        )
        user = create_user()
        event_booking = create_booking(user, event_stock, is_used=False)
        PcObject.save(event_booking)

        # When
        number_of_bookings = get_all_used_bookings_count()

        # Then
        assert number_of_bookings == 0


class GetAllCancelledBookingsCountTest:
    @clean_database
    def test_returns_0_if_no_cancelled_bookings(self, app):
        # Given
        less_than_48_hours_ago = datetime.utcnow() - timedelta(hours=47)
        offerer = create_offerer()
        venue = create_venue(offerer)
        event_offer = create_offer_with_event_product(venue)
        event_stock = create_stock(
            offer=event_offer,
            price=0,
            beginning_datetime=less_than_48_hours_ago,
            end_datetime=less_than_48_hours_ago + timedelta(hours=1),
            booking_limit_datetime=less_than_48_hours_ago - timedelta(hours=1)
        )
        user = create_user()
        booking = create_booking(user, event_stock, is_cancelled=False)
        PcObject.save(booking)

        # When
        number_of_bookings = get_all_cancelled_bookings_count()

        # Then
        assert number_of_bookings == 0

    @clean_database
    def test_returns_0_if_no_cancelled_bookings(self, app):
        # Given
        less_than_48_hours_ago = datetime.utcnow() - timedelta(hours=47)
        offerer = create_offerer()
        venue = create_venue(offerer)
        event_offer = create_offer_with_event_product(venue)
        event_stock = create_stock(
            offer=event_offer,
            price=0,
            beginning_datetime=less_than_48_hours_ago,
            end_datetime=less_than_48_hours_ago + timedelta(hours=1),
            booking_limit_datetime=less_than_48_hours_ago - timedelta(hours=1)
        )
        user = create_user()
        booking = create_booking(user, event_stock, is_cancelled=True)
        PcObject.save(booking)

        # When
        number_of_bookings = get_all_cancelled_bookings_count()

        # Then
        assert number_of_bookings == 1


class QueryGetOfferCountsPerTypeAndMediumTest:
    @clean_database
    def test_returns_2_cinema_physical_1_musique_physical_and_1_musique_digital_when_offers_with_stock_and_user_offerer(
            self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        user_offerer = create_user_offerer(user, offerer)
        virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
        physical_venue = create_venue(offerer, is_virtual=False)
        offer_cinema1 = create_offer_with_event_product(physical_venue, event_type=EventType.CINEMA)
        offer_cinema2 = create_offer_with_event_product(physical_venue, event_type=EventType.CINEMA)
        offer_musique_digital = create_offer_with_thing_product(virtual_venue, url='http://url.test',
                                                                thing_type=ThingType.MUSIQUE)
        offer_musique_physical = create_offer_with_thing_product(physical_venue, thing_type=ThingType.MUSIQUE)
        stock_cinema1 = create_stock(offer=offer_cinema1)
        stock_cinema2 = create_stock(offer=offer_cinema2)
        stock_musique_digital = create_stock(offer=offer_musique_digital)
        stock_musique_physical = create_stock(offer=offer_musique_physical)
        PcObject.save(stock_cinema1, stock_cinema2, stock_musique_digital, stock_musique_physical, user_offerer)

        # When
        offer_counts = _query_get_offer_counts_grouped_by_type_and_medium().fetchall()

        # Then
        assert len(offer_counts) == 3
        assert ('EventType.CINEMA', False, 2) in offer_counts
        assert ('ThingType.MUSIQUE', False, 1) in offer_counts
        assert ('ThingType.MUSIQUE', True, 1) in offer_counts

    @clean_database
    def test_returns_nothing_when_no_stock(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        user_offerer = create_user_offerer(user, offerer)
        virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
        physical_venue = create_venue(offerer, is_virtual=False)
        offer_cinema1 = create_offer_with_event_product(physical_venue, event_type=EventType.CINEMA)
        offer_cinema2 = create_offer_with_event_product(physical_venue, event_type=EventType.CINEMA)
        offer_musique_digital = create_offer_with_thing_product(virtual_venue, url='http://url.test',
                                                                thing_type=ThingType.MUSIQUE)
        offer_musique_physical = create_offer_with_thing_product(physical_venue, thing_type=ThingType.MUSIQUE)
        PcObject.save(offer_cinema1, offer_cinema2, offer_musique_digital, offer_musique_physical, user_offerer)

        # When
        offer_counts = _query_get_offer_counts_grouped_by_type_and_medium().fetchall()

        # Then
        assert offer_counts == []

    @clean_database
    def test_returns_nothing_if_no_user_offerer(self, app):
        # Given
        offerer = create_offerer()
        virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
        physical_venue = create_venue(offerer, is_virtual=False)
        offer_cinema1 = create_offer_with_event_product(physical_venue, event_type=EventType.CINEMA)
        offer_cinema2 = create_offer_with_event_product(physical_venue, event_type=EventType.CINEMA)
        offer_musique_digital = create_offer_with_thing_product(virtual_venue, url='http://url.test',
                                                                thing_type=ThingType.MUSIQUE)
        offer_musique_physical = create_offer_with_thing_product(physical_venue, thing_type=ThingType.MUSIQUE)
        stock_cinema1 = create_stock(offer=offer_cinema1)
        stock_cinema2 = create_stock(offer=offer_cinema2)
        stock_musique_digital = create_stock(offer=offer_musique_digital)
        stock_musique_physical = create_stock(offer=offer_musique_physical)
        PcObject.save(stock_cinema1, stock_cinema2, stock_musique_digital, stock_musique_physical)

        # When
        offer_counts = _query_get_offer_counts_grouped_by_type_and_medium().fetchall()

        # Then
        assert offer_counts == []


class GetOffersByTypeAndDigitalTableTest:
    @clean_database
    def test_returns_table_with_columns_type_and_digital_ordered_by_type_then_digital(self, app):
        # Given
        expected_dataframe = pandas.read_csv('tests/scripts/dashboard/offers_by_type_and_digital.csv')

        # When
        type_and_digital_dataframe = _get_offers_grouped_by_type_and_medium()

        # Then
        print(expected_dataframe)
        assert type_and_digital_dataframe.equals(expected_dataframe)


class GetCountsByTypeAndDigitalCountsTest:
    @clean_database
    def test_returns_offers_ordered_by_counts_then_type_name_then_support(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        user_offerer = create_user_offerer(user, offerer)
        virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
        physical_venue = create_venue(offerer, is_virtual=False)
        offer_cinema1 = create_offer_with_event_product(physical_venue, event_type=EventType.CINEMA)
        offer_cinema2 = create_offer_with_event_product(physical_venue, event_type=EventType.CINEMA)
        offer_musique_digital = create_offer_with_thing_product(virtual_venue, url='http://url.test',
                                                                thing_type=ThingType.MUSIQUE)
        offer_musique_physical = create_offer_with_thing_product(physical_venue, thing_type=ThingType.MUSIQUE)
        stock_cinema1 = create_stock(offer=offer_cinema1)
        stock_cinema2 = create_stock(offer=offer_cinema2)
        stock_musique_digital = create_stock(offer=offer_musique_digital)
        stock_musique_physical = create_stock(offer=offer_musique_physical)
        PcObject.save(stock_cinema1, stock_cinema2, stock_musique_digital, stock_musique_physical, user_offerer)

        expected_dataframe = pandas.read_csv('tests/scripts/dashboard/offers_by_type_and_digital_counts.csv')

        # When
        offers_by_type_and_digital_counts = _get_counts_grouped_by_type_and_medium(_query_get_offer_counts_grouped_by_type_and_medium,
                                                                           'Nombre d\'offres')

        # Then
        assert offers_by_type_and_digital_counts.eq(expected_dataframe).all().all()

    @clean_database
    def test_returns_bookings_ordered_by_counts_then_type_name_then_support(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        user_booking = create_user(email='booking@test.com')
        user_offerer = create_user_offerer(user, offerer)
        virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
        physical_venue = create_venue(offerer, is_virtual=False)
        offer_cinema1 = create_offer_with_event_product(physical_venue, event_type=EventType.CINEMA)
        offer_cinema2 = create_offer_with_event_product(physical_venue, event_type=EventType.CINEMA)
        offer_musique_digital = create_offer_with_thing_product(virtual_venue, url='http://url.test',
                                                                thing_type=ThingType.MUSIQUE)
        offer_musique_physical = create_offer_with_thing_product(physical_venue, thing_type=ThingType.MUSIQUE)
        stock_cinema1 = create_stock(offer=offer_cinema1, price=0)
        stock_cinema2 = create_stock(offer=offer_cinema2, price=0)
        stock_musique_digital = create_stock(offer=offer_musique_digital, price=0)
        stock_musique_physical = create_stock(offer=offer_musique_physical, price=0)
        booking_musique_physical1 = create_booking(user_booking, stock_musique_physical)
        booking_musique_physical2 = create_booking(user_booking, stock_musique_physical, quantity=2)
        booking_musique_digital = create_booking(user_booking, stock_musique_digital)
        PcObject.save(stock_cinema1, stock_cinema2, booking_musique_physical1, booking_musique_physical2,
                      booking_musique_digital, user_offerer)

        expected_dataframe = pandas.read_csv('tests/scripts/dashboard/bookings_by_type_and_medium_counts.csv')

        # When
        bookings_by_type_and_digital_counts = _get_counts_grouped_by_type_and_medium(_query_get_booking_counts_grouped_by_type_and_medium, 'Nombre de réservations')

        # Then
        assert bookings_by_type_and_digital_counts.equals(expected_dataframe)


class QueryGetBookingCountsPerTypeAndDigitalTest:
    @clean_database
    def test_returns_3_musique_physical_1_musique_digital_when_bookings_with_user_offerer(
            self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        user_booking = create_user(email='booking@test.com')
        user_offerer = create_user_offerer(user, offerer)
        virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
        physical_venue = create_venue(offerer, is_virtual=False)
        offer_cinema1 = create_offer_with_event_product(physical_venue, event_type=EventType.CINEMA)
        offer_cinema2 = create_offer_with_event_product(physical_venue, event_type=EventType.CINEMA)
        offer_musique_digital = create_offer_with_thing_product(virtual_venue, url='http://url.test',
                                                                thing_type=ThingType.MUSIQUE)
        offer_musique_physical = create_offer_with_thing_product(physical_venue, thing_type=ThingType.MUSIQUE)
        stock_cinema1 = create_stock(offer=offer_cinema1, price=0)
        stock_cinema2 = create_stock(offer=offer_cinema2, price=0)
        stock_musique_digital = create_stock(offer=offer_musique_digital, price=0)
        stock_musique_physical = create_stock(offer=offer_musique_physical, price=0)
        booking_musique_physical1 = create_booking(user_booking, stock_musique_physical)
        booking_musique_physical2 = create_booking(user_booking, stock_musique_physical, quantity=2)
        booking_musique_digital = create_booking(user_booking, stock_musique_digital)
        PcObject.save(stock_cinema1, stock_cinema2, booking_musique_physical1, booking_musique_physical2,
                      booking_musique_digital, user_offerer)

        # When
        booking_counts = _query_get_booking_counts_grouped_by_type_and_medium().fetchall()

        # Then
        assert len(booking_counts) == 2
        assert ('ThingType.MUSIQUE', False, 3) in booking_counts
        assert ('ThingType.MUSIQUE', True, 1) in booking_counts

    @clean_database
    def test_returns_nothing_when_cancelled_booking(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        user_booking = create_user(email='booking@test.com')
        user_offerer = create_user_offerer(user, offerer)
        physical_venue = create_venue(offerer, is_virtual=False)
        offer = create_offer_with_event_product(physical_venue, event_type=EventType.CINEMA)
        stock = create_stock(offer=offer, price=0)
        cancelled_booking = create_booking(user_booking, stock, is_cancelled=True)
        PcObject.save(offer, user_offerer, cancelled_booking)

        # When
        booking_counts = _query_get_booking_counts_grouped_by_type_and_medium().fetchall()

        # Then
        assert booking_counts == []

    @clean_database
    def test_returns_nothing_if_no_user_offerer(self, app):
        # Given
        offerer = create_offerer()
        user_booking = create_user(email='booking@test.com')
        virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
        physical_venue = create_venue(offerer, is_virtual=False)
        offer_cinema1 = create_offer_with_event_product(physical_venue, event_type=EventType.CINEMA)
        offer_cinema2 = create_offer_with_event_product(physical_venue, event_type=EventType.CINEMA)
        offer_musique_digital = create_offer_with_thing_product(virtual_venue, url='http://url.test',
                                                                thing_type=ThingType.MUSIQUE)
        offer_musique_physical = create_offer_with_thing_product(physical_venue, thing_type=ThingType.MUSIQUE)
        stock_cinema1 = create_stock(offer=offer_cinema1, price=0)
        stock_cinema2 = create_stock(offer=offer_cinema2, price=0)
        stock_musique_digital = create_stock(offer=offer_musique_digital, price=0)
        stock_musique_physical = create_stock(offer=offer_musique_physical, price=0)
        booking_musique_physical1 = create_booking(user_booking, stock_musique_physical)
        booking_musique_physical2 = create_booking(user_booking, stock_musique_physical, quantity=2)
        booking_musique_digital = create_booking(user_booking, stock_musique_digital)
        PcObject.save(stock_cinema1, stock_cinema2, booking_musique_physical1, booking_musique_physical2,
                      booking_musique_digital)

        # When
        booking_counts = _query_get_booking_counts_grouped_by_type_and_medium().fetchall()

        # Then
        assert booking_counts == []
