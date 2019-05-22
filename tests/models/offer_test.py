from datetime import datetime, timedelta
from pprint import pprint

import pytest

from models import Offer, PcObject, ApiErrors, ThingType, EventType, Product
from tests.conftest import clean_database
from tests.test_utils import create_booking, create_user
from tests.test_utils import create_offer_with_event_product, create_product_with_Event_type
from tests.test_utils import create_product_with_Thing_type, create_offer_with_thing_product, create_offerer, \
    create_stock, create_venue
from utils.date import DateTimes

now = datetime.utcnow()
two_days_ago = now - timedelta(days=2)
four_days_ago = now - timedelta(days=4)
five_days_from_now = now + timedelta(days=5)
ten_days_from_now = now + timedelta(days=10)


@pytest.mark.standalone
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
        offer_dict = offer._asdict(include=["dateRange"])

        # Then
        assert offer_dict['dateRange'] == ['2018-10-22T10:10:10Z', '2018-10-22T13:10:10Z']

    def test_is_empty_if_offer_is_on_a_thing(self):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)

        # then
        assert offer.dateRange == DateTimes()

    def test_matches_the_occurrence_if_only_one_occurrence(self):
        # given
        offer = create_offer_with_event_product()
        offer.stocks = [
            create_stock(offer, beginning_datetime=two_days_ago, end_datetime=five_days_from_now)
        ]

        # then
        assert offer.dateRange == DateTimes(two_days_ago, five_days_from_now)

    def test_starts_at_first_beginning_date_time_and_ends_at_last_end_date_time(self):
        # given
        offer = create_offer_with_event_product()
        offer.stocks = [
            create_stock(offer, beginning_datetime=two_days_ago, end_datetime=five_days_from_now),
            create_stock(offer, beginning_datetime=four_days_ago, end_datetime=five_days_from_now),
            create_stock(offer, beginning_datetime=four_days_ago, end_datetime=ten_days_from_now),
            create_stock(offer, beginning_datetime=two_days_ago, end_datetime=ten_days_from_now)
        ]

        # then
        assert offer.dateRange == DateTimes(four_days_ago, ten_days_from_now)
        assert offer.dateRange.datetimes == [four_days_ago, ten_days_from_now]

    def test_is_empty_if_event_has_no_event_occurrences(self):
        # given
        offer = create_offer_with_event_product()
        offer.stocks = []

        # then
        assert offer.dateRange == DateTimes()


@pytest.mark.standalone
class CreateOfferTest:
    @clean_database
    def test_success_when_is_digital_and_virtual_venue(self, app):
        # Given
        url = 'http://mygame.fr/offre'
        digital_thing = create_product_with_Thing_type(thing_type=ThingType.JEUX_VIDEO, url=url, is_national=True)
        offerer = create_offerer()
        virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
        PcObject.check_and_save(virtual_venue)

        offer = create_offer_with_thing_product(virtual_venue, digital_thing)

        # When
        PcObject.check_and_save(digital_thing, offer)

        # Then
        assert offer.url == url

    @clean_database
    def test_success_when_is_physical_and_physical_venue(self, app):
        # Given
        physical_thing = create_product_with_Thing_type(thing_type=ThingType.LIVRE_EDITION, url=None)
        offerer = create_offerer()
        physical_venue = create_venue(offerer, is_virtual=False, siret=offerer.siren + '12345')
        PcObject.check_and_save(physical_venue)

        offer = create_offer_with_thing_product(physical_venue, physical_thing)

        # When
        PcObject.check_and_save(physical_thing, offer)

        # Then
        assert offer.url is None

    @clean_database
    def test_fails_when_is_digital_but_physical_venue(self, app):
        # Given
        digital_thing = create_product_with_Thing_type(thing_type=ThingType.JEUX_VIDEO, url='http://mygame.fr/offre')
        offerer = create_offerer()
        physical_venue = create_venue(offerer)
        PcObject.check_and_save(physical_venue)
        offer = create_offer_with_thing_product(physical_venue, digital_thing)

        # When
        with pytest.raises(ApiErrors) as errors:
            PcObject.check_and_save(offer)

        # Then
        assert errors.value.errors['venue'] == [
            'Une offre numérique doit obligatoirement être associée au lieu "Offre en ligne"']

    @clean_database
    def test_fails_when_is_physical_but_venue_is_virtual(self, app):
        # Given
        physical_thing = create_product_with_Thing_type(thing_type=ThingType.JEUX_VIDEO, url=None)
        offerer = create_offerer()
        digital_venue = create_venue(offerer, is_virtual=True, siret=None)
        PcObject.check_and_save(digital_venue)
        offer = create_offer_with_thing_product(digital_venue, physical_thing)

        # When
        with pytest.raises(ApiErrors) as errors:
            PcObject.check_and_save(offer)

        # Then
        assert errors.value.errors['venue'] == [
            'Une offre physique ne peut être associée au lieu "Offre en ligne"']

    @clean_database
    def test_fails_when_is_event_but_durationMinute_is_empty(self, app):
        # Given
        event_product = create_product_with_Event_type(duration_minutes=None)
        offerer = create_offerer()
        venue = create_venue(offerer)
        PcObject.check_and_save(venue)
        offer = create_offer_with_event_product(venue, event_product)

        # When
        with pytest.raises(ApiErrors) as errors:
            PcObject.check_and_save(offer)

        # Then
        assert errors.value.errors['durationMinutes'] == [
            'Une offre de type évènement doit avoir une durée en minute']

    def test_offer_is_marked_as_isevent_property(self):
        # Given
        physical_thing = create_product_with_Thing_type(thing_type=ThingType.JEUX_VIDEO, url=None)
        offerer = create_offerer()
        digital_venue = create_venue(offerer, is_virtual=True, siret=None)

        # When
        offer = create_offer_with_thing_product(digital_venue, physical_thing)
        pprint(Offer.type)

        # Then
        assert offer.isEvent == False
        assert offer.isThing == True

    def test_offer_is_marked_as_isthing_property(self):
        # Given
        event_product = create_product_with_Event_type(event_type=EventType.CINEMA)
        offerer = create_offerer()
        digital_venue = create_venue(offerer, is_virtual=False, siret=None)

        # When
        offer = create_offer_with_thing_product(digital_venue, event_product)
        pprint(Offer.type)

        # Then
        assert offer.isEvent == True
        assert offer.isThing == False

    def test_offer_is_neither_event_nor_thing(self):
        # Given
        event_product = Product()
        offerer = create_offerer()
        digital_venue = create_venue(offerer, is_virtual=False, siret=None)

        # When
        offer = create_offer_with_thing_product(digital_venue, event_product)
        pprint(Offer.type)

        # Then
        assert offer.isEvent == False
        assert offer.isThing == False


    @clean_database
    def test_create_digital_offer_success(self, app):
        # Given
        url = 'http://mygame.fr/offre'
        digital_thing = create_product_with_Thing_type(thing_type=ThingType.JEUX_VIDEO, url=url, is_national=True)
        offerer = create_offerer()
        virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
        PcObject.check_and_save(virtual_venue)

        offer = create_offer_with_thing_product(virtual_venue, digital_thing)

        # When
        PcObject.check_and_save(digital_thing, offer)

        # Then
        assert offer.product.url == url

    @clean_database
    def test_offer_error_when_thing_is_digital_but_venue_not_virtual(self, app):
        # Given
        digital_thing = create_product_with_Thing_type(thing_type=ThingType.JEUX_VIDEO, url='http://mygame.fr/offre')
        offerer = create_offerer()
        physical_venue = create_venue(offerer)
        PcObject.check_and_save(physical_venue)
        offer = create_offer_with_thing_product(physical_venue, digital_thing)

        # When
        with pytest.raises(ApiErrors) as errors:
            PcObject.check_and_save(offer)

        # Then
        assert errors.value.errors['venue'] == [
            'Une offre numérique doit obligatoirement être associée au lieu "Offre en ligne"']


def test_offer_is_digital_if_it_has_an_url():
    # given
    offer = Offer()
    offer.url = 'http://url.com'

    # when / then
    assert offer.isDigital


def test_thing_offer_offerType_returns_dict_matching_ThingType_enum():
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_thing_product(venue, thing_type=ThingType.LIVRE_EDITION)
    expected_value = {
        'conditionalFields': ["author", "isbn"],
        'proLabel': 'Livre - format papier ou numérique, abonnements lecture',
        'appLabel': 'Livres, cartes bibliothèque ou médiathèque',
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': 'Lire',
        'description': 'S’abonner à un quotidien d’actualité ?'
                       ' À un hebdomadaire humoristique ? '
                       'À un mensuel dédié à la nature ? '
                       'Acheter une BD ou un manga ? '
                       'Ou tout simplement ce livre dont tout le monde parle ?',
        'value': 'ThingType.LIVRE_EDITION',
        'type': 'Thing'
    }

    # when
    offer_type = offer.offerType

    # then
    assert offer_type == expected_value


def test_event_offer_offerType_returns_dict_matching_EventType_enum():
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue, event_type=EventType.SPECTACLE_VIVANT)
    expected_value = {
        'conditionalFields': ["author", "showType", "stageDirector", "performer"],
        'proLabel': "Spectacle vivant",
        'appLabel': 'Spectacle vivant',
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Applaudir",
        'description': "Suivre un géant de 12 mètres dans la ville ? "
                       "Rire aux éclats devant un stand up ?"
                       " Rêver le temps d’un opéra ou d’un spectacle de danse ? "
                       "Assister à une pièce de théâtre, ou se laisser conter une histoire ?",
        'value': 'EventType.SPECTACLE_VIVANT',
        'type': 'Event'
    }

    # when
    offer_type = offer.offerType

    # then
    assert offer_type == expected_value


def test_thing_offer_offerType_returns_None_if_type_does_not_match_ThingType_enum():
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_thing_product(venue, thing_type='')

    # when
    offer_type = offer.offerType

    # then
    assert offer_type == None


def test_event_offer_offerType_returns_None_if_type_does_not_match_EventType_enum():
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue, event_type='Workshop')

    # when
    offer_type = offer.offerType

    # then
    assert offer_type == None


@pytest.mark.standalone
class IsFullyBookedTest:
    def test_returns_true_if_all_available_stocks_are_booked(self):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        user = create_user()
        stock1 = create_stock(available=2)
        stock2 = create_stock(available=1)
        create_booking(user, stock=stock1, quantity=1)
        create_booking(user, stock=stock1, quantity=1)
        create_booking(user, stock=stock2, quantity=1)
        offer.stocks = [stock1, stock2]

        # then
        assert offer.isFullyBooked is True

    def test_returns_true_ignoring_cancelled_bookings(self):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        user = create_user()
        stock1 = create_stock(available=2)
        stock2 = create_stock(available=1)
        create_booking(user, stock=stock1, quantity=1)
        create_booking(user, stock=stock1, quantity=1, is_cancelled=True)
        create_booking(user, stock=stock2, quantity=1)
        offer.stocks = [stock1, stock2]

        # then
        assert offer.isFullyBooked is False

    def test_stocks_with_past_booking_limit_datetimes_are_ignored(self):
        # given
        offer = Offer()
        user = create_user()
        stock1 = create_stock(available=2, booking_limit_datetime=datetime.utcnow() - timedelta(weeks=3))
        stock2 = create_stock(available=1)
        stock3 = create_stock(available=1)
        create_booking(user, stock=stock2, quantity=1)
        create_booking(user, stock=stock3, quantity=1)
        offer.stocks = [stock1, stock2, stock3]

        # then
        assert offer.isFullyBooked is True

    def test_returns_false_if_stocks_have_none_available_quantity(self):
        # given
        offer = Offer()
        user = create_user()
        stock1 = create_stock(available=None)
        stock2 = create_stock(available=None)
        create_booking(user, stock=stock1, quantity=1)
        create_booking(user, stock=stock2, quantity=1)
        offer.stocks = [stock1, stock2]

        # then
        assert offer.isFullyBooked is False


@pytest.mark.standalone
class IsFinishedTest:
    def test_returns_true_if_all_stocks_have_past_booking_limit_datetime(self):
        # given
        now = datetime.utcnow()
        offer = Offer()
        stock1 = create_stock(booking_limit_datetime=now - timedelta(weeks=3))
        stock2 = create_stock(booking_limit_datetime=now - timedelta(weeks=2))
        stock3 = create_stock(booking_limit_datetime=now - timedelta(weeks=1))
        offer.stocks = [stock1, stock2, stock3]

        # then
        assert offer.isFinished is True

    def test_returns_false_if_any_stock_has_future_booking_limit_datetime(self):
        # given
        now = datetime.utcnow()
        offer = Offer()
        stock1 = create_stock(booking_limit_datetime=now - timedelta(weeks=3))
        stock2 = create_stock(booking_limit_datetime=None)
        stock3 = create_stock(booking_limit_datetime=now + timedelta(weeks=1))
        offer.stocks = [stock1, stock2, stock3]

        # then
        assert offer.isFinished is False

    def test_returns_false_if_all_stocks_have_no_booking_limit_datetime(self):
        # given
        offer = Offer()
        stock1 = create_stock(booking_limit_datetime=None)
        stock2 = create_stock(booking_limit_datetime=None)
        stock3 = create_stock(booking_limit_datetime=None)
        offer.stocks = [stock1, stock2, stock3]

        # then
        assert offer.isFinished is False


@pytest.mark.standalone
def test_date_range_is_empty_if_offer_is_on_a_thing():
    # given
    offer = Offer()
    offer.product = create_product_with_Thing_type()
    offer.stocks = []

    # then
    assert offer.dateRange == DateTimes()


@pytest.mark.standalone
def test_date_range_matches_the_occurrence_if_only_one_occurrence():
    # given
    offer = Offer()
    offer.product = create_product_with_Event_type()
    offer.stocks = [
        create_stock(offer=offer, beginning_datetime=two_days_ago, end_datetime=five_days_from_now)
    ]

    # then
    assert offer.dateRange == DateTimes(two_days_ago, five_days_from_now)


@pytest.mark.standalone
def test_date_range_starts_at_first_beginning_date_time_and_ends_at_last_end_date_time():
    # given
    offer = Offer()
    offer.product = create_product_with_Event_type()
    offer.stocks = [
        create_stock(offer=offer, beginning_datetime=two_days_ago, end_datetime=five_days_from_now),
        create_stock(offer=offer, beginning_datetime=four_days_ago, end_datetime=five_days_from_now),
        create_stock(offer=offer, beginning_datetime=four_days_ago, end_datetime=ten_days_from_now),
        create_stock(offer=offer, beginning_datetime=two_days_ago, end_datetime=ten_days_from_now)
    ]

    # then
    assert offer.dateRange == DateTimes(four_days_ago, ten_days_from_now)
    assert offer.dateRange.datetimes == [four_days_ago, ten_days_from_now]


@pytest.mark.standalone
def test_date_range_is_empty_if_event_has_no_stocks():
    # given
    offer = Offer()
    offer.product = create_product_with_Event_type()
    offer.stocks = []

    # then
    assert offer.dateRange == DateTimes()
