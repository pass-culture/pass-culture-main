from datetime import datetime, timedelta

import pytest

from models import Offer, ApiErrors, ThingType, EventType, Product, Provider
from repository import repository
from routes.serialization import as_dict
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_booking, create_criterion, create_user, create_stock, \
    create_offerer, \
    create_venue, create_deposit, create_recommendation, create_mediation
from tests.model_creators.specific_creators import create_stock_from_offer, create_product_with_thing_type, \
    create_product_with_event_type, create_offer_with_thing_product, create_offer_with_event_product
from utils.date import DateTimes

now = datetime.utcnow()
two_days_ago = now - timedelta(days=2)
four_days_ago = now - timedelta(days=4)
five_days_from_now = now + timedelta(days=5)
ten_days_from_now = now + timedelta(days=10)


class AddStockAlertMessageToOfferTest:
    class ThingOfferTest:
        @clean_database
        def test_check_offer_with_no_stock(self, app):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue=venue)

            repository.save(user, offer)

            # when
            result = offer.stockAlertMessage

            # then
            assert result == 'pas encore de stock'

        @clean_database
        def test_check_offer_with_all_stocks_unlimited(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue=venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=None)
            stock2 = create_stock_from_offer(offer, available=None)

            deposit = create_deposit(user2, amount=500)
            booking = create_booking(user=user2, stock=stock, venue=venue, recommendation=recommendation, quantity=3)

            repository.save(booking, deposit, user, offer, stock, stock2, user2)

            # when
            result = offer.stockAlertMessage

            # then
            assert result == 'illimité'

        @clean_database
        def test_check_offer_with_one_unlimited_and_one_available_zero_stock(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue=venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=None)
            stock2 = create_stock_from_offer(offer, available=0)

            deposit = create_deposit(user2, amount=500)
            booking = create_booking(user=user2, stock=stock, venue=venue, recommendation=recommendation, quantity=3)

            repository.save(booking, deposit, user, offer, stock, stock2, user2)

            # when
            result = offer.stockAlertMessage

            # then
            assert result == 'plus de stock pour 2 offres'

        @clean_database
        def test_check_offer_with_one_available_zero_and_one_sold_out_stock(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue=venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=3)
            stock2 = create_stock_from_offer(offer, available=0)

            deposit = create_deposit(user2, amount=500)
            booking = create_booking(user=user2, stock=stock, venue=venue, recommendation=recommendation, quantity=3)

            repository.save(booking, deposit, user, offer, stock, stock2, user2)

            # when
            result = offer.stockAlertMessage

            # then
            assert result == 'plus de stock'

        @clean_database
        def test_check_offer_with_all_sold_out_stocks(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue=venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=3)
            stock2 = create_stock_from_offer(offer, available=10)

            deposit = create_deposit(user2, amount=500)
            booking = create_booking(user=user2, stock=stock, venue=venue, recommendation=recommendation, quantity=3)
            booking2 = create_booking(user=user2, stock=stock2, venue=venue, recommendation=recommendation, quantity=10)

            repository.save(booking, booking2, deposit, user,
                            offer, stock, stock2, user2)

            # when
            result = offer.stockAlertMessage

            # then
            assert result == 'plus de stock'

        @clean_database
        def test_check_offer_with_all_remaining_stocks(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue=venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=10)
            stock2 = create_stock_from_offer(offer, available=150)

            deposit = create_deposit(user2, amount=500)
            booking = create_booking(user=user2, stock=stock, venue=venue, recommendation=recommendation, quantity=3)
            booking2 = create_booking(user=user2, stock=stock2, venue=venue, recommendation=recommendation, quantity=20)

            repository.save(booking, booking2, deposit, user,
                            offer, stock, stock2, user2)

            # when
            result = offer.stockAlertMessage

            # then
            assert result == 'encore 137 en stock'

        @clean_database
        def test_check_offer_with_one_sold_out_and_one_remaining_stock(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue=venue)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer, available=8)
            stock2 = create_stock_from_offer(offer, available=10)

            deposit = create_deposit(user2, amount=500)
            booking = create_booking(user=user2, stock=stock2, venue=venue, recommendation=recommendation, quantity=10)

            repository.save(booking, deposit, user, offer, stock, stock2, user2)

            # when
            result = offer.stockAlertMessage

            # then
            assert result == 'plus de stock pour 1 offre'

        @clean_database
        def test_check_offer_with_two_sold_out_one_unlimited_and_one_remaining_stocks(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue=venue)
            recommendation = create_recommendation(offer, user)

            stock = create_stock_from_offer(offer, available=10)
            stock2 = create_stock_from_offer(offer, available=5)
            stock3 = create_stock_from_offer(offer, available=1)
            stock4 = create_stock_from_offer(offer, available=None)

            deposit = create_deposit(user2, amount=500)
            booking = create_booking(user=user2, stock=stock2, venue=venue, recommendation=recommendation, quantity=5)
            booking2 = create_booking(user=user2, stock=stock3, venue=venue, recommendation=recommendation, quantity=1)

            repository.save(booking, booking2, deposit, user, offer,
                            stock, stock2, stock3, stock4, user2)

            # when
            result = offer.stockAlertMessage

            # then
            assert result == 'plus de stock pour 3 offres'

    class EventOfferTest:
        @clean_database
        def test_check_offer_with_no_stock(self, app):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)

            repository.save(user, offer)

            # when
            result = offer.stockAlertMessage

            # then
            assert result == 'pas encore de places'

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

            deposit = create_deposit(user2, amount=500)
            booking = create_booking(user=user2, stock=stock, venue=venue, recommendation=recommendation, quantity=3)

            repository.save(booking, deposit, user, offer, stock, stock2, user2)

            # when
            result = offer.stockAlertMessage

            # then
            assert result == 'illimité'

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

            deposit = create_deposit(user2, amount=500)
            booking = create_booking(user=user2, stock=stock, venue=venue, recommendation=recommendation, quantity=3)

            repository.save(booking, deposit, user, offer, stock, stock2, user2)

            # when
            result = offer.stockAlertMessage

            # then
            assert result == 'plus de places pour 2 offres'

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

            deposit = create_deposit(user2, amount=500)
            booking = create_booking(user=user2, stock=stock, venue=venue, recommendation=recommendation, quantity=3)

            repository.save(booking, deposit, user, offer, stock, stock2, user2)

            # when
            result = offer.stockAlertMessage

            # then
            assert result == 'plus de places pour toutes les dates'

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

            deposit = create_deposit(user2, amount=500)
            booking = create_booking(user=user2, stock=stock, venue=venue, recommendation=recommendation, quantity=3)
            booking2 = create_booking(user=user2, stock=stock2, venue=venue, recommendation=recommendation, quantity=10)

            repository.save(booking, booking2, deposit, user,
                            offer, stock, stock2, user2)

            # when
            result = offer.stockAlertMessage

            # then
            assert result == 'plus de places pour toutes les dates'

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

            deposit = create_deposit(user2, amount=500)
            booking = create_booking(user=user2, stock=stock, venue=venue, recommendation=recommendation, quantity=3)
            booking2 = create_booking(user=user2, stock=stock2, venue=venue, recommendation=recommendation, quantity=11)

            repository.save(booking, booking2, deposit, user,
                            offer, stock, stock2, user2)

            # when
            result = offer.stockAlertMessage

            # then
            assert result == 'encore 36 places'

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

            deposit = create_deposit(user2, amount=500)
            booking = create_booking(user=user2, stock=stock2, venue=venue, recommendation=recommendation, quantity=10)

            repository.save(booking, deposit, user, offer, stock, stock2, user2)

            # when
            result = offer.stockAlertMessage

            # then
            assert result == 'plus de places pour 1 offre'

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

            deposit = create_deposit(user2, amount=500)
            booking = create_booking(user=user2, stock=stock2, venue=venue, recommendation=recommendation, quantity=5)
            booking2 = create_booking(user=user2, stock=stock3, venue=venue, recommendation=recommendation, quantity=1)

            repository.save(booking, booking2, deposit, user, offer,
                            stock, stock2, stock3, stock4, user2)

            # when
            result = offer.stockAlertMessage

            # then
            assert result == 'plus de places pour 3 offres'

        @clean_database
        def test_check_offer_with_used_stocks_before_stock_last_update(self, app):
            # given
            user = create_user(email='user@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            recommendation = create_recommendation(offer, user)

            stock = create_stock_from_offer(
                offer, available=5, date_modified=datetime.utcnow())

            deposit = create_deposit(user2, amount=500)
            booking = create_booking(user=user2, stock=stock, venue=venue, recommendation=recommendation, is_used=True,
                                     quantity=5)

            repository.save(booking, deposit, user, offer, stock, user2)

            # when
            result = offer.stockAlertMessage

            # then
            assert result == 'encore 5 places'


class BaseScoreTest:
    @clean_database
    def test_offer_base_score_with_no_criteria(self):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        offer.criteria = []
        repository.save(offer)

        # Then
        assert offer.baseScore == 0

    @clean_database
    def test_offer_base_score_with_multiple_criteria(self):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        offer.criteria = [create_criterion(name='negative', score_delta=-1),
                          create_criterion(name='positive', score_delta=2)]
        repository.save(offer)

        # Then
        assert offer.baseScore == 1


class DateRangeTest:
    def test_offer_as_dict_returns_dateRange_in_ISO_8601(self):
        # Given
        offer = Offer()
        offer.stocks = [
            create_stock(offer=offer,
                         beginning_datetime=datetime(2018, 10, 22, 10, 10, 10),
                         end_datetime=datetime(2018, 10, 22, 13, 10, 10))
        ]

        # When
        offer_dict = as_dict(offer, includes=["dateRange"])

        # Then
        assert offer_dict['dateRange'] == [
            '2018-10-22T10:10:10Z', '2018-10-22T13:10:10Z']

    def test_is_empty_when_offer_is_on_a_thing(self):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue=venue)

        # then
        assert offer.dateRange == DateTimes()

    def test_matches_the_occurrence_when_only_one_occurrence(self):
        # given
        offer = create_offer_with_event_product()
        offer.stocks = [
            create_stock(offer, beginning_datetime=two_days_ago,
                         end_datetime=five_days_from_now)
        ]

        # then
        assert offer.dateRange == DateTimes(two_days_ago, five_days_from_now)

    def test_starts_at_first_beginning_date_time_and_ends_at_last_end_date_time(self):
        # given
        offer = create_offer_with_event_product()
        offer.stocks = [
            create_stock(offer, beginning_datetime=four_days_ago,
                         end_datetime=five_days_from_now),
            create_stock(offer, beginning_datetime=four_days_ago,
                         end_datetime=ten_days_from_now),
            create_stock(offer, beginning_datetime=two_days_ago,
                         end_datetime=five_days_from_now),
            create_stock(offer, beginning_datetime=two_days_ago,
                         end_datetime=ten_days_from_now)
        ]

        # then
        assert offer.dateRange == DateTimes(four_days_ago, ten_days_from_now)
        assert offer.dateRange.datetimes == [four_days_ago, ten_days_from_now]

    def test_ignores_soft_deleted_occurences(self):
        # given
        offer = create_offer_with_event_product()
        offer.stocks = [
            create_stock(offer, beginning_datetime=four_days_ago, end_datetime=five_days_from_now,
                         is_soft_deleted=True),
            create_stock(offer, beginning_datetime=two_days_ago,
                         end_datetime=five_days_from_now),
            create_stock(offer, beginning_datetime=two_days_ago,
                         end_datetime=ten_days_from_now)
        ]

        # then
        assert offer.dateRange == DateTimes(two_days_ago, ten_days_from_now)
        assert offer.dateRange.datetimes == [two_days_ago, ten_days_from_now]

    def test_is_empty_when_event_has_no_event_occurrences(self):
        # given
        offer = create_offer_with_event_product()
        offer.stocks = []

        # then
        assert offer.dateRange == DateTimes()

    def test_is_empty_when_event_only_has_a_soft_deleted_occurence(self):
        # given
        offer = create_offer_with_event_product()
        offer.stocks = [
            create_stock(offer, beginning_datetime=two_days_ago,
                         end_datetime=five_days_from_now, is_soft_deleted=True),
        ]

        # then
        assert offer.dateRange == DateTimes()


class CreateOfferTest:
    @clean_database
    def test_success_when_is_digital_and_virtual_venue(self, app):
        # Given
        url = 'http://mygame.fr/offre'
        digital_thing = create_product_with_thing_type(thing_type=ThingType.JEUX_VIDEO, url=url, is_national=True)
        offerer = create_offerer()
        virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
        repository.save(virtual_venue)
        offer = create_offer_with_thing_product(venue=virtual_venue, product=digital_thing)

        # When
        repository.save(digital_thing, offer)

        # Then
        assert offer.url == url

    @clean_database
    def test_success_when_is_physical_and_physical_venue(self, app):
        # Given
        physical_thing = create_product_with_thing_type(
            thing_type=ThingType.LIVRE_EDITION, url=None)
        offerer = create_offerer()
        physical_venue = create_venue(
            offerer, is_virtual=False, siret=offerer.siren + '12345')
        repository.save(physical_venue)

        offer = create_offer_with_thing_product(venue=physical_venue, product=physical_thing)

        # When
        repository.save(physical_thing, offer)

        # Then
        assert offer.url is None

    @clean_database
    def test_fails_when_is_digital_but_physical_venue(self, app):
        # Given
        digital_thing = create_product_with_thing_type(
            thing_type=ThingType.JEUX_VIDEO, url='http://mygame.fr/offre')
        offerer = create_offerer()
        physical_venue = create_venue(offerer)
        repository.save(physical_venue)
        offer = create_offer_with_thing_product(venue=physical_venue, product=digital_thing)

        # When
        with pytest.raises(ApiErrors) as errors:
            repository.save(offer)

        # Then
        assert errors.value.errors['venue'] == [
            'Une offre numérique doit obligatoirement être associée au lieu "Offre numérique"']

    @clean_database
    def test_fails_when_is_physical_but_venue_is_virtual(self, app):
        # Given
        physical_thing = create_product_with_thing_type(
            thing_type=ThingType.JEUX_VIDEO, url=None)
        offerer = create_offerer()
        digital_venue = create_venue(offerer, is_virtual=True, siret=None)
        repository.save(digital_venue)
        offer = create_offer_with_thing_product(venue=digital_venue, product=physical_thing)

        # When
        with pytest.raises(ApiErrors) as errors:
            repository.save(offer)

        # Then
        assert errors.value.errors['venue'] == [
            'Une offre physique ne peut être associée au lieu "Offre numérique"']

    @clean_database
    def test_success_when_is_event_but_durationMinute_is_empty(self, app):
        # Given
        event_product = create_product_with_event_type(duration_minutes=None)
        offerer = create_offerer()
        venue = create_venue(offerer)
        repository.save(venue)
        offer = create_offer_with_event_product(venue=venue, product=event_product)

        # When
        repository.save(offer)

        # Then
        assert offer.durationMinutes is None
        assert offer.product.durationMinutes is None

    @clean_database
    def test_offer_is_marked_as_isevent_property(self):
        # Given
        physical_thing = create_product_with_thing_type(
            thing_type=ThingType.JEUX_VIDEO, url=None)
        offerer = create_offerer()
        digital_venue = create_venue(offerer, is_virtual=True, siret=None)

        # When
        offer = create_offer_with_thing_product(venue=digital_venue, product=physical_thing)

        # Then
        assert offer.isEvent == False
        assert offer.isThing == True

    def test_offer_is_marked_as_isthing_property(self):
        # Given
        event_product = create_product_with_event_type(
            event_type=EventType.CINEMA)
        offerer = create_offerer()
        digital_venue = create_venue(offerer, is_virtual=False, siret=None)

        # When
        offer = create_offer_with_thing_product(venue=digital_venue, product=event_product)

        # Then
        assert offer.isEvent == True
        assert offer.isThing == False

    def test_offer_is_neither_event_nor_thing(self):
        # Given
        event_product = Product()
        offerer = create_offerer()
        digital_venue = create_venue(offerer, is_virtual=False, siret=None)

        # When
        offer = create_offer_with_thing_product(venue=digital_venue, product=event_product)

        # Then
        assert offer.isEvent == False
        assert offer.isThing == False

    @clean_database
    def test_create_digital_offer_success(self, app):
        # Given
        url = 'http://mygame.fr/offre'
        digital_thing = create_product_with_thing_type(
            thing_type=ThingType.JEUX_VIDEO, url=url, is_national=True)
        offerer = create_offerer()
        virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
        repository.save(virtual_venue)

        offer = create_offer_with_thing_product(venue=virtual_venue, product=digital_thing)

        # When
        repository.save(digital_thing, offer)

        # Then
        assert offer.product.url == url

    @clean_database
    def test_offer_error_when_thing_is_digital_but_venue_not_virtual(self, app):
        # Given
        digital_thing = create_product_with_thing_type(
            thing_type=ThingType.JEUX_VIDEO, url='http://mygame.fr/offre')
        offerer = create_offerer()
        physical_venue = create_venue(offerer)
        repository.save(physical_venue)
        offer = create_offer_with_thing_product(venue=physical_venue, product=digital_thing)

        # When
        with pytest.raises(ApiErrors) as errors:
            repository.save(offer)

        # Then
        assert errors.value.errors['venue'] == [
            'Une offre numérique doit obligatoirement être associée au lieu "Offre numérique"']


def test_offer_is_digital_when_it_has_an_url():
    # given
    offer = Offer()
    offer.url = 'http://url.com'

    # when / then
    assert offer.isDigital


def test_thing_offer_offerType_returns_dict_matching_ThingType_enum():
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_thing_product(
        venue=venue, thing_type=ThingType.LIVRE_EDITION)
    expected_value = {
        'conditionalFields': ["author", "isbn"],
        'proLabel': 'Livres papier ou numérique, abonnements lecture',
        'appLabel': 'Livre ou carte lecture',
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': 'Lire',
        'description': 'S’abonner à un quotidien d’actualité ?'
                       ' À un hebdomadaire humoristique ? '
                       'À un mensuel dédié à la nature ? '
                       'Acheter une BD ou un manga ? '
                       'Ou tout simplement ce livre dont tout le monde parle ?',
        'value': 'ThingType.LIVRE_EDITION',
        'type': 'Thing',
        'isActive': True
    }

    # when
    offer_type = offer.offerType

    # then
    assert offer_type == expected_value


def test_event_offer_offerType_returns_dict_matching_EventType_enum():
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(
        venue, event_type=EventType.SPECTACLE_VIVANT)
    expected_value = {
        'conditionalFields': ["author", "showType", "stageDirector", "performer"],
        'proLabel': "Spectacle vivant",
        'appLabel': 'Spectacle',
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Applaudir",
        'description': "Suivre un géant de 12 mètres dans la ville ? "
                       "Rire aux éclats devant un stand up ?"
                       " Rêver le temps d’un opéra ou d’un spectacle de danse ? "
                       "Assister à une pièce de théâtre, ou se laisser conter une histoire ?",
        'value': 'EventType.SPECTACLE_VIVANT',
        'type': 'Event',
        'isActive': True
    }

    # when
    offer_type = offer.offerType

    # then
    assert offer_type == expected_value


def test_thing_offer_offerType_returns_None_when_type_does_not_match_ThingType_enum():
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_thing_product(venue=venue, thing_type='')

    # when
    offer_type = offer.offerType

    # then
    assert offer_type == None


def test_event_offer_offerType_returns_None_when_type_does_not_match_EventType_enum():
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue, event_type='Workshop')

    # when
    offer_type = offer.offerType

    # then
    assert offer_type == None


class IsFullyBookedTest:
    def test_returns_true_when_all_available_stocks_are_booked_after_last_update(self):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue=venue)
        user = create_user()
        stock1 = create_stock(available=2, date_modified=datetime(2019, 1, 1))
        stock2 = create_stock(available=1, date_modified=datetime(2019, 1, 1))
        create_booking(user=user, date_used=datetime(2019, 2, 1), is_used=True, quantity=1, stock=stock1)
        create_booking(user=user, date_used=datetime(2019, 2, 1), is_used=True, quantity=1, stock=stock1)
        create_booking(user=user, date_used=datetime(2019, 2, 1), is_used=True, quantity=1, stock=stock2)
        offer.stocks = [stock1, stock2]

        # then
        assert offer.isFullyBooked is True

    def test_returns_true_ignoring_cancelled_bookings(self):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue=venue)
        user = create_user()
        stock1 = create_stock(available=2)
        stock2 = create_stock(available=1)
        create_booking(user=user, quantity=1, stock=stock1)
        create_booking(user=user, is_cancelled=True, quantity=1, stock=stock1)
        create_booking(user=user, quantity=1, stock=stock2)
        offer.stocks = [stock1, stock2]

        # then
        assert offer.isFullyBooked is False

    def test_stocks_with_passed_booking_limit_datetimes_are_ignored(self):
        # given
        offer = Offer()
        user = create_user()
        stock1 = create_stock(
            available=2, booking_limit_datetime=datetime.utcnow() - timedelta(weeks=3))
        stock2 = create_stock(available=1, date_modified=datetime(2019, 1, 1))
        stock3 = create_stock(available=1, date_modified=datetime(2019, 1, 1))
        create_booking(user=user, date_used=datetime(2019, 2, 1), is_used=True, quantity=1, stock=stock2)
        create_booking(user=user, date_used=datetime(2019, 2, 1), is_used=True, quantity=1, stock=stock3)
        offer.stocks = [stock1, stock2, stock3]

        # then
        assert offer.isFullyBooked is True

    def test_returns_false_when_stocks_have_none_available_quantity(self):
        # given
        offer = Offer()
        user = create_user()
        stock1 = create_stock(available=None)
        stock2 = create_stock(available=None)
        create_booking(user=user, quantity=1, stock=stock1)
        create_booking(user=user, quantity=1, stock=stock2)
        offer.stocks = [stock1, stock2]

        # then
        assert offer.isFullyBooked is False

    def test_returns_false_when_stocks_are_booked_before_last_update(self):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue=venue)
        user = create_user()
        stock1 = create_stock(available=2, date_modified=datetime(2019, 1, 1))
        create_booking(user=user, date_used=datetime(2018, 1, 1), is_used=True, quantity=1, stock=stock1)
        create_booking(user=user, date_used=datetime(2019, 2, 1), is_used=True, quantity=1, stock=stock1)
        offer.stocks = [stock1]

        # then
        assert offer.isFullyBooked is False


class hasBookingLimitDatetimesPassedTest:
    def test_returns_true_when_all_stocks_have_passed_booking_limit_datetime(self):
        # given
        now = datetime.utcnow()
        offer = Offer()
        stock1 = create_stock(booking_limit_datetime=now - timedelta(weeks=3))
        stock2 = create_stock(booking_limit_datetime=now - timedelta(weeks=2))
        stock3 = create_stock(booking_limit_datetime=now - timedelta(weeks=1))
        offer.stocks = [stock1, stock2, stock3]

        # then
        assert offer.hasBookingLimitDatetimesPassed is True

    def test_returns_false_when_any_stock_has_future_booking_limit_datetime(self):
        # given
        now = datetime.utcnow()
        offer = Offer()
        stock1 = create_stock(booking_limit_datetime=now - timedelta(weeks=3))
        stock2 = create_stock(booking_limit_datetime=None)
        stock3 = create_stock(booking_limit_datetime=now + timedelta(weeks=1))
        offer.stocks = [stock1, stock2, stock3]

        # then
        assert offer.hasBookingLimitDatetimesPassed is False

    def test_returns_false_when_all_stocks_have_no_booking_limit_datetime(self):
        # given
        offer = Offer()
        stock1 = create_stock(booking_limit_datetime=None)
        stock2 = create_stock(booking_limit_datetime=None)
        stock3 = create_stock(booking_limit_datetime=None)
        offer.stocks = [stock1, stock2, stock3]

        # then
        assert offer.hasBookingLimitDatetimesPassed is False

class IsNotBookableTest:
    def test_returns_true_when_all_stocks_have_passed_booking_limit_datetime(self):
        # given
        now = datetime.utcnow()
        offer = Offer()
        stock1 = create_stock(booking_limit_datetime=now - timedelta(weeks=3))
        stock2 = create_stock(booking_limit_datetime=now - timedelta(weeks=2))
        stock3 = create_stock(booking_limit_datetime=now - timedelta(weeks=1))
        offer.stocks = [stock1, stock2, stock3]

        # then
        assert offer.isNotBookable

    def test_returns_false_when_any_stock_has_future_booking_limit_datetime(self):
        # given
        now = datetime.utcnow()
        offer = Offer()
        stock1 = create_stock(booking_limit_datetime=now - timedelta(weeks=3))
        stock2 = create_stock(booking_limit_datetime=None)
        stock3 = create_stock(booking_limit_datetime=now + timedelta(weeks=1))
        offer.stocks = [stock1, stock2, stock3]

        # then
        assert not offer.isNotBookable

    def test_returns_false_when_all_stocks_have_no_booking_limit_datetime(self):
        # given
        offer = Offer()
        stock1 = create_stock(booking_limit_datetime=None)
        stock2 = create_stock(booking_limit_datetime=None)
        stock3 = create_stock(booking_limit_datetime=None)
        offer.stocks = [stock1, stock2, stock3]

        # then
        assert not offer.isNotBookable

class ActiveMediationTest:
    def test_returns_none_when_no_mediations_exist_on_offer(self):
        # given
        offer = Offer()
        offer.mediations = []

        # then
        assert offer.activeMediation is None

    def test_returns_none_when_all_mediations_are_deactivated(self):
        # given
        offer = Offer()
        offer.mediations = [
            create_mediation(offer, is_active=False),
            create_mediation(offer, is_active=False)
        ]

        # then
        assert offer.activeMediation is None

    def test_returns_the_most_recent_active_mediation(self):
        # given
        offer = Offer()
        offer.mediations = [
            create_mediation(offer, front_text='1st',
                             date_created=four_days_ago, is_active=True),
            create_mediation(offer, front_text='2nd',
                             date_created=now, is_active=False),
            create_mediation(offer, front_text='3rd',
                             date_created=two_days_ago, is_active=True)
        ]

        # then
        assert offer.activeMediation.frontText == '3rd'


class DateRangeTest:
    def test_date_range_is_empty_when_offer_is_a_thing(self):
        # Given
        offer = Offer()
        offer.type = str(ThingType.LIVRE_EDITION)
        offer.stocks = [create_stock(offer=offer)]

        # When / Then
        assert offer.dateRange == DateTimes()

    def test_date_range_matches_the_occurrence_when_offer_has_only_one_stock(self):
        # Given
        offer = Offer()
        offer.type = str(EventType.CINEMA)
        offer.stocks = [
            create_stock(offer=offer,
                         beginning_datetime=two_days_ago,
                         end_datetime=five_days_from_now)
        ]

        # When / Then
        assert offer.dateRange == DateTimes(two_days_ago, five_days_from_now)

    def test_date_range_starts_at_first_beginning_date_time_and_ends_at_last_end_date_time(self):
        # Given
        offer = Offer()
        offer.type = str(EventType.CINEMA)
        offer.stocks = [
            create_stock(offer=offer, beginning_datetime=two_days_ago,
                         end_datetime=five_days_from_now),
            create_stock(offer=offer, beginning_datetime=four_days_ago,
                         end_datetime=five_days_from_now),
            create_stock(offer=offer, beginning_datetime=four_days_ago,
                         end_datetime=ten_days_from_now),
            create_stock(offer=offer, beginning_datetime=two_days_ago,
                         end_datetime=ten_days_from_now)
        ]

        # When / Then
        assert offer.dateRange == DateTimes(four_days_ago, ten_days_from_now)

    def test_date_range_is_empty_when_event_has_no_stocks(self):
        # given
        offer = Offer()
        offer.type = str(EventType.CINEMA)
        offer.stocks = []

        # then
        assert offer.dateRange == DateTimes()


class IsEditableTest:
    def test_returns_false_when_offer_is_coming_from_provider(self, app):
        # given
        offer = Offer()
        offer.lastProviderId = 21

        # then
        assert offer.isEditable is False

    def test_returns_false_when_offer_is_coming_from_TiteLive_provider(self, app):
        # given
        provider = Provider()
        provider.name = 'myProvider'
        provider.localClass = 'TiteLive is my class'
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue=venue)
        offer.lastProviderId = 21
        offer.lastProvider = provider

        # then
        assert offer.isEditable is False

    def test_returns_true_when_offer_is_coming_from_Allocine_provider(self, app):
        # given
        provider = Provider()
        provider.name = 'my allocine provider'
        provider.localClass = 'AllocineStocks'
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        offer.lastProviderId = 22
        offer.lastProvider = provider

        # then
        assert offer.isEditable is True

    def test_returns_true_when_offer_is_not_coming_from_provider(self, app):
        # given
        offer = Offer()

        # then
        assert offer.isEditable is True


class ActiveStocksTest:
    def test_should_return_only_not_soft_deleted_stocks(self):
        # Given
        offer = Offer()
        active_stock = create_stock(offer=offer, is_soft_deleted=False)
        soft_deleted_stock = create_stock(offer=offer, is_soft_deleted=True)
        offer.stocks = [
            soft_deleted_stock,
            active_stock,
        ]

        # When / Then
        assert offer.activeStocks == [active_stock]


class IsFromProviderTest:
    def test_returns_True_when_offer_is_coming_from_provider(self, app):
        # given
        offer = Offer()
        offer.lastProviderId = 21

        # then
        assert offer.isFromProvider is True

    def test_returns_True_when_offer_is_coming_from_TiteLive_provider(self, app):
        # given
        provider = Provider()
        provider.name = 'myProvider'
        provider.localClass = 'TiteLive is my class'
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue=venue)
        offer.lastProviderId = 21
        offer.lastProvider = provider

        # then
        assert offer.isFromProvider is True

    def test_returns_False_when_offer_is_not_coming_from_provider(self, app):
        # given
        offer = Offer()

        # then
        assert offer.isFromProvider is False


class ThumbUrlTest:
    def test_should_return_thumb_url_with_mediation_when_mediation_exists(self):
        # given
        offer = Offer()
        offer.mediations = [create_mediation(idx=1, date_created=datetime(2019, 11, 1, 10, 0, 0), thumb_count=1)]

        # then
        assert offer.thumb_url == 'http://localhost/storage/thumbs/mediations/AE'

    def test_should_return_thumb_url_with_product_when_mediation_does_not_exist(self):
        # given
        offer = Offer()
        offer.product = create_product_with_thing_type()
        offer.product.id = 1

        # then
        assert offer.thumb_url == 'http://localhost/storage/thumbs/products/AE'

    def test_should_return_empty_thumb_url_when_no_product_nor_mediation(self):
        # given
        offer = Offer()

        # then
        assert offer.thumb_url == ''
