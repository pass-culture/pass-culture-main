from datetime import datetime, timedelta

import pytest

from models import OfferSQLEntity, ApiErrors, ThingType, EventType, Product, Provider
from repository import repository
from routes.serialization import as_dict
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_booking, create_user, create_stock, \
    create_offerer, \
    create_venue, create_mediation
from tests.model_creators.specific_creators import create_product_with_thing_type, \
    create_product_with_event_type, create_offer_with_thing_product, create_offer_with_event_product
from utils.date import DateTimes

now = datetime.utcnow()
two_days_ago = now - timedelta(days=2)
four_days_ago = now - timedelta(days=4)
five_days_from_now = now + timedelta(days=5)
ten_days_from_now = now + timedelta(days=10)


class DateRangeTest:
    def test_offer_as_dict_returns_dateRange_in_ISO_8601(self):
        # Given
        offer = OfferSQLEntity()
        offer.stocks = [
            create_stock(beginning_datetime=datetime(2018, 10, 22, 10, 10, 10), offer=offer)
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
            create_stock(beginning_datetime=two_days_ago, offer=offer)
        ]

        # then
        assert offer.dateRange == DateTimes(two_days_ago, five_days_from_now)

    def test_starts_at_first_beginning_date_time(self):
        # given
        offer = create_offer_with_event_product()
        offer.stocks = [
            create_stock(beginning_datetime=four_days_ago, offer=offer),
            create_stock(beginning_datetime=four_days_ago, offer=offer),
            create_stock(beginning_datetime=two_days_ago, offer=offer),
            create_stock(beginning_datetime=two_days_ago, offer=offer)
        ]

        # then
        assert offer.dateRange == DateTimes(four_days_ago, ten_days_from_now)
        assert offer.dateRange.datetimes == [four_days_ago, ten_days_from_now]

    def test_ignores_soft_deleted_occurences(self):
        # given
        offer = create_offer_with_event_product()
        offer.stocks = [
            create_stock(beginning_datetime=four_days_ago, is_soft_deleted=True, offer=offer),
            create_stock(beginning_datetime=two_days_ago, offer=offer),
            create_stock(beginning_datetime=two_days_ago, offer=offer)
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
            create_stock(beginning_datetime=two_days_ago, is_soft_deleted=True, offer=offer),
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
    offer = OfferSQLEntity()
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
    def test_should_be_fully_booked_when_all_active_stocks_are_booked(self):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue=venue)
        stock1 = create_stock(date_modified=datetime(2019, 1, 1), quantity=None, is_soft_deleted=True)
        stock2 = create_stock(date_modified=datetime(2019, 1, 1), quantity=0,)
        offer.stocks = [stock1, stock2]

        # then
        assert offer.isFullyBooked is True

    def test_should_be_fully_booked_when_all_available_stocks_are_booked_after_last_update(self):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue=venue)
        user = create_user()
        stock1 = create_stock(date_modified=datetime(2019, 1, 1), quantity=2)
        stock2 = create_stock(date_modified=datetime(2019, 1, 1), quantity=1)
        create_booking(user=user, date_used=datetime(2019, 2, 1), is_used=True, quantity=1, stock=stock1)
        create_booking(user=user, date_used=datetime(2019, 2, 1), is_used=True, quantity=1, stock=stock1)
        create_booking(user=user, date_used=datetime(2019, 2, 1), is_used=True, quantity=1, stock=stock2)
        offer.stocks = [stock1, stock2]

        # then
        assert offer.isFullyBooked is True

    def test_should_not_be_fully_booked_ignoring_cancelled_bookings(self):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue=venue)
        user = create_user()
        stock1 = create_stock(quantity=2)
        stock2 = create_stock(quantity=1)
        create_booking(user=user, quantity=1, stock=stock1)
        create_booking(user=user, is_cancelled=True, quantity=1, stock=stock1)
        create_booking(user=user, quantity=1, stock=stock2)
        offer.stocks = [stock1, stock2]

        # then
        assert offer.isFullyBooked is False

    def test_stocks_with_passed_booking_limit_datetimes_are_ignored(self):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue=venue)
        user = create_user()

        expired_stock = create_stock(booking_limit_datetime=datetime.utcnow() - timedelta(weeks=3), quantity=2)
        booked_stock = create_stock(date_modified=datetime(2019, 1, 1), quantity=1)

        create_booking(user=user, date_used=datetime(2019, 2, 1), is_used=True, quantity=1, stock=booked_stock)
        offer.stocks = [expired_stock, booked_stock]

        # then
        assert offer.isFullyBooked is True

    def test_returns_false_when_stocks_have_none_available_quantity(self):
        # given
        offer = OfferSQLEntity()
        user = create_user()
        stock1 = create_stock(quantity=None)
        stock2 = create_stock(quantity=None)
        create_booking(user=user, quantity=1, stock=stock1)
        create_booking(user=user, quantity=1, stock=stock2)
        offer.stocks = [stock1, stock2]

        # then
        assert offer.isFullyBooked is False


class hasBookingLimitDatetimesPassedTest:
    def test_returns_false_when_no_active_stock_has_future_booking_limit_datetime(self):
        # given
        now = datetime.utcnow()
        offer = OfferSQLEntity()
        stock1 = create_stock(booking_limit_datetime=now - timedelta(weeks=3))
        stock2 = create_stock(booking_limit_datetime=now + timedelta(weeks=2), is_soft_deleted=True)
        offer.stocks = [stock1, stock2]

        # then
        assert offer.hasBookingLimitDatetimesPassed

    def test_returns_true_when_all_stocks_have_passed_booking_limit_datetime(self):
        # given
        now = datetime.utcnow()
        offer = OfferSQLEntity()
        stock1 = create_stock(booking_limit_datetime=now - timedelta(weeks=3))
        stock2 = create_stock(booking_limit_datetime=now - timedelta(weeks=2))
        stock3 = create_stock(booking_limit_datetime=now - timedelta(weeks=1))
        offer.stocks = [stock1, stock2, stock3]

        # then
        assert offer.hasBookingLimitDatetimesPassed

    def test_returns_false_when_any_stock_has_future_booking_limit_datetime(self):
        # given
        now = datetime.utcnow()

        offer = OfferSQLEntity()
        stock1 = create_stock(booking_limit_datetime=now - timedelta(weeks=3))
        stock2 = create_stock(booking_limit_datetime=None)
        stock3 = create_stock(booking_limit_datetime=now + timedelta(weeks=1))
        offer.stocks = [stock1, stock2, stock3]

        # then
        assert not offer.hasBookingLimitDatetimesPassed

    def test_returns_false_when_all_stocks_have_no_booking_limit_datetime(self):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue=venue)

        stock1 = create_stock(booking_limit_datetime=None)
        stock2 = create_stock(booking_limit_datetime=None)
        stock3 = create_stock(booking_limit_datetime=None)
        offer.stocks = [stock1, stock2, stock3]

        # then
        assert not offer.hasBookingLimitDatetimesPassed


class ActiveMediationTest:
    def test_returns_none_when_no_mediations_exist_on_offer(self):
        # given
        offer = OfferSQLEntity()
        offer.mediations = []

        # then
        assert offer.activeMediation is None

    def test_returns_none_when_all_mediations_are_deactivated(self):
        # given
        offer = OfferSQLEntity()
        offer.mediations = [
            create_mediation(offer, is_active=False),
            create_mediation(offer, is_active=False)
        ]

        # then
        assert offer.activeMediation is None

    def test_returns_the_most_recent_active_mediation(self):
        # given
        offer = OfferSQLEntity()
        offer.mediations = [
            create_mediation(offer, date_created=four_days_ago, is_active=True),
            create_mediation(offer, date_created=now, is_active=False),
            create_mediation(offer, date_created=two_days_ago, is_active=True)
        ]

        # then
        assert offer.activeMediation.dateCreated == two_days_ago


class DateRangeTest:
    def test_date_range_is_empty_when_offer_is_a_thing(self):
        # Given
        offer = OfferSQLEntity()
        offer.type = str(ThingType.LIVRE_EDITION)
        offer.stocks = [create_stock(offer=offer)]

        # When / Then
        assert offer.dateRange == DateTimes()

    def test_date_range_starts_and_ends_at_beginning_date_time_when_offer_has_only_one_stock(self):
        # Given
        offer = OfferSQLEntity()
        offer.type = str(EventType.CINEMA)
        offer.stocks = [
            create_stock(beginning_datetime=two_days_ago, offer=offer)
        ]

        # When / Then
        assert offer.dateRange == DateTimes(two_days_ago, two_days_ago)

    def test_date_range_starts_at_first_beginning_date_time_and_ends_at_last_beginning_date_time(self):
        # Given
        offer = OfferSQLEntity()
        offer.type = str(EventType.CINEMA)
        offer.stocks = [
            create_stock(beginning_datetime=two_days_ago, offer=offer),
            create_stock(beginning_datetime=four_days_ago, offer=offer),
            create_stock(beginning_datetime=four_days_ago, offer=offer),
            create_stock(beginning_datetime=two_days_ago, offer=offer)
        ]

        # When / Then
        assert offer.dateRange == DateTimes(four_days_ago, two_days_ago)

    def test_date_range_is_empty_when_event_has_no_stocks(self):
        # given
        offer = OfferSQLEntity()
        offer.type = str(EventType.CINEMA)
        offer.stocks = []

        # then
        assert offer.dateRange == DateTimes()


class IsEditableTest:
    def test_returns_false_when_offer_is_coming_from_provider(self, app):
        # given
        offer = OfferSQLEntity()
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
        offer = OfferSQLEntity()

        # then
        assert offer.isEditable is True


class ActiveStocksTest:
    def test_should_return_only_not_soft_deleted_stocks(self):
        # Given
        offer = OfferSQLEntity()
        active_stock = create_stock(is_soft_deleted=False, offer=offer)
        soft_deleted_stock = create_stock(is_soft_deleted=True, offer=offer)
        offer.stocks = [
            soft_deleted_stock,
            active_stock,
        ]

        # When / Then
        assert offer.activeStocks == [active_stock]


class IsFromProviderTest:
    def test_returns_True_when_offer_is_coming_from_provider(self, app):
        # given
        offer = OfferSQLEntity()
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
        offer = OfferSQLEntity()

        # then
        assert offer.isFromProvider is False


class ThumbUrlTest:
    def test_should_return_thumb_url_with_mediation_when_mediation_exists(self):
        # given
        offer = OfferSQLEntity()
        offer.mediations = [create_mediation(idx=1, date_created=datetime(2019, 11, 1, 10, 0, 0), thumb_count=1)]

        # then
        assert offer.thumbUrl == 'http://localhost/storage/thumbs/mediations/AE'

    def test_should_return_thumb_url_with_product_when_mediation_does_not_exist(self):
        # given
        offer = OfferSQLEntity()
        offer.product = create_product_with_thing_type()
        offer.product.id = 1

        # then
        assert offer.thumbUrl == 'http://localhost/storage/thumbs/products/AE'

    def test_should_return_empty_thumb_url_when_no_product_nor_mediation(self):
        # given
        offer = OfferSQLEntity()

        # then
        assert offer.thumbUrl == ''


class OfferTypeTest:
    @clean_database
    def test_should_return_matching_category_given_offer_app_label(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(thing_type=ThingType.JEUX, venue=venue)
        repository.save(offer)

        # When
        category = offer.offer_category

        # Then
        assert category == 'JEUX_VIDEO'
