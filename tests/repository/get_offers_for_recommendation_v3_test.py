from datetime import datetime, timedelta

from shapely.geometry import Polygon

from models import DiscoveryView, ThingType, EventType
from repository import repository
from repository.offer_queries import get_offers_for_recommendation_v3
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_user, create_venue, create_mediation, \
    create_iris, create_iris_venue, create_booking, create_criterion, create_favorite
from tests.model_creators.specific_creators import create_product_with_thing_type, create_stock_from_offer, \
    create_offer_with_thing_product, create_stock_with_thing_offer, create_stock_with_event_offer, \
    create_offer_with_event_product
from tests.test_utils import POLYGON_TEST


class GetOffersForRecommendationV3Test:
    @clean_database
    def test_should_not_return_activation_event(self, app):
        # Given
        offerer = create_offerer(siren='123456789')
        user = create_user()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        offer_activation = create_offer_with_event_product(venue, event_type=EventType.ACTIVATION)

        stock = create_stock_from_offer(offer)
        stock_activation = create_stock_from_offer(offer_activation)
        mediation1 = create_mediation(stock.offer)
        mediation2 = create_mediation(stock_activation.offer)


        repository.save(user, stock, stock_activation, mediation1, mediation2)

        DiscoveryView.refresh(concurrently=False)

        # When
        offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

        # Then
        assert offer in offers
        assert offer_activation not in offers

    @clean_database
    def test_should_not_return_activation_thing(self, app):
        # Given
        offerer = create_offerer(siren='123456789')
        user = create_user()
        venue_93 = create_venue(offerer, postal_code='93000', departement_code='93', siret=offerer.siren + '33333')
        offer_93 = create_offer_with_thing_product(venue_93, thumb_count=1)
        offer_activation_93 = create_offer_with_thing_product(venue_93, thing_type=ThingType.ACTIVATION,
                                                              thumb_count=1)
        stock_93 = create_stock_from_offer(offer_93)
        stock_activation_93 = create_stock_from_offer(offer_activation_93)
        create_mediation(stock_93.offer)
        create_mediation(stock_activation_93.offer)

        repository.save(user, stock_93, stock_activation_93)

        DiscoveryView.refresh(concurrently=False)

        # When
        offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

        # Then
        assert offer_93 in offers
        assert offer_activation_93 not in offers

    @clean_database
    def test_should_return_offers_with_stock(self, app):
        # Given
        product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34', longitude=2.295695,
                             latitude=49.894171)
        offer = create_offer_with_thing_product(venue=venue, product=product)
        stock = create_stock_from_offer(offer, available=2)
        create_mediation(stock.offer)

        repository.save(user, stock)

        DiscoveryView.refresh(concurrently=False)

        # When
        offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

        # Then
        assert len(offers) == 1

    @clean_database
    def test_should_return_offers_with_mediation_only(app):
        # Given
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')
        stock1 = create_stock_with_thing_offer(offerer, venue, name='thing_with_mediation')
        stock2 = create_stock_with_thing_offer(offerer, venue, name='thing_without_mediation')
        create_mediation(stock1.offer)

        repository.save(user, stock1, stock2)


        DiscoveryView.refresh(concurrently=False)

        # When
        offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

        # Then
        assert len(offers) == 1
        assert offers[0].name == 'thing_with_mediation'

    @clean_database
    def test_should_return_offers_that_occur_in_less_than_10_days_and_things_first(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')

        stock1 = create_stock_with_thing_offer(offerer, venue, name='thing')
        stock2 = create_stock_with_event_offer(offerer,
                                               venue,
                                               beginning_datetime=datetime.utcnow() + timedelta(days=4),
                                               end_datetime=datetime.utcnow() + timedelta(days=4, hours=2),
                                               name='event_occurs_soon',
                                               thumb_count=1)
        stock3 = create_stock_with_event_offer(offerer,
                                               venue,
                                               beginning_datetime=datetime.utcnow() + timedelta(days=11),
                                               end_datetime=datetime.utcnow() + timedelta(days=11, hours=2),
                                               name='event_occurs_later',
                                               thumb_count=1)
        create_mediation(stock1.offer)
        create_mediation(stock2.offer)
        create_mediation(stock3.offer)

        repository.save(user, stock1, stock2, stock3)

        DiscoveryView.refresh(concurrently=False)

        # When
        offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

        # Then
        assert len(offers) == 3
        assert (offers[0].name == 'event_occurs_soon'
                and offers[1].name == 'thing') \
               or (offers[1].name == 'event_occurs_soon'
                   and offers[0].name == 'thing')
        assert offers[2].name == 'event_occurs_later'

    @clean_database
    def test_should_return_offers_with_varying_types(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')
        stock1 = create_stock_with_thing_offer(offerer, venue, name='thing', thing_type=ThingType.JEUX_VIDEO)
        stock2 = create_stock_with_thing_offer(offerer, venue, name='thing', thing_type=ThingType.CINEMA_ABO,
                                               url='http://example.com')
        stock3 = create_stock_with_thing_offer(offerer, venue, name='thing', thing_type=ThingType.JEUX_VIDEO)
        stock4 = create_stock_with_thing_offer(offerer, venue, name='thing', thing_type=ThingType.JEUX_VIDEO)
        stock5 = create_stock_with_thing_offer(offerer, venue, name='thing', thing_type=ThingType.AUDIOVISUEL)
        stock6 = create_stock_with_thing_offer(offerer, venue, name='thing', thing_type=ThingType.JEUX)
        create_mediation(stock1.offer)
        create_mediation(stock2.offer)
        create_mediation(stock3.offer)
        create_mediation(stock4.offer)
        create_mediation(stock5.offer)
        create_mediation(stock6.offer)

        repository.save(user, stock1, stock2, stock3, stock4, stock5, stock6, user)

        DiscoveryView.refresh(concurrently=False)

        def _first_four_offers_have_different_type_and_onlineness(offers):
            return len(set([o.type + (o.url or '')
                            for o in offers[:4]])) == 4

        # When
        offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

        # Then
        assert len(offers) == 6
        assert _first_four_offers_have_different_type_and_onlineness(offers)

    @clean_database
    def test_should_not_return_offers_with_no_stock(self, app):
        # Given
        product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')
        offer = create_offer_with_thing_product(venue=venue, product=product)
        stock = create_stock_from_offer(offer, available=2, price=0)
        booking1 = create_booking(user=user, stock=stock, is_cancelled=True, quantity=2, venue=venue)
        booking2 = create_booking(user=user, stock=stock, quantity=2, venue=venue)
        create_mediation(stock.offer)

        repository.save(user, booking1, booking2)

        DiscoveryView.refresh(concurrently=False)

        # When
        offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

        # Then
        assert len(offers) == 0

    @clean_database
    def test_with_criteria_should_return_offer_with_highest_base_score_first(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')

        offer1 = create_offer_with_thing_product(venue, thing_type=ThingType.JEUX_VIDEO, thumb_count=1)
        stock1 = create_stock_from_offer(offer1, price=0)
        offer1.criteria = [create_criterion(name='negative', score_delta=-1)]

        offer2 = create_offer_with_thing_product(venue, thing_type=ThingType.JEUX_VIDEO, thumb_count=1)
        stock2 = create_stock_from_offer(offer2, price=0)
        offer2.criteria = [create_criterion(name='positive', score_delta=1)]

        create_mediation(stock1.offer)
        create_mediation(stock2.offer)

        repository.save(user, stock1, stock2)

        DiscoveryView.refresh(concurrently=False)

        # When
        offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

        # Then
        assert offers == [offer2, offer1]

    @clean_database
    def test_with_criteria_should_return_offer_with_highest_base_score_first_bust_keep_the_partition(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')

        offer1 = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO, thumb_count=1)
        stock1 = create_stock_from_offer(offer1, price=0)
        offer1.criteria = [create_criterion(name='negative', score_delta=1)]

        offer2 = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO, thumb_count=1)
        stock2 = create_stock_from_offer(offer2, price=0)
        offer2.criteria = [create_criterion(name='positive', score_delta=2)]

        offer3 = create_offer_with_thing_product(venue, thing_type=ThingType.JEUX_VIDEO, thumb_count=1)
        stock3 = create_stock_from_offer(offer3, price=0)
        offer3.criteria = []

        create_mediation(stock1.offer)
        create_mediation(stock2.offer)
        create_mediation(stock3.offer)

        repository.save(user, stock1, stock2, stock3)

        DiscoveryView.refresh(concurrently=False)

        # When
        offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

        # Then
        assert offers == [offer2, offer3, offer1]

    @clean_database
    def test_should_not_return_booked_offers(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')
        offer = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
        stock = create_stock_from_offer(offer, price=0)
        user = create_user()
        booking = create_booking(user=user, stock=stock)
        create_mediation(stock.offer)

        repository.save(user, booking)

        DiscoveryView.refresh(concurrently=False)

        # When
        offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

        # Then
        assert offers == []

    @clean_database
    def test_should_not_return_favorite_offers(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')

        offer = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
        stock = create_stock_from_offer(offer, price=0)
        mediation = create_mediation(stock.offer)
        favorite = create_favorite(mediation=mediation, offer=offer, user=user)

        repository.save(user, favorite)

        DiscoveryView.refresh(concurrently=False)

        # When
        offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

        # Then
        assert offers == []

    @clean_database
    def test_should_not_return_offers_having_only_soft_deleted_stocks(self, app):
        # Given
        product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34', longitude=2.295695,
                             latitude=49.894171)
        offer = create_offer_with_thing_product(venue=venue, product=product)
        stock = create_stock_from_offer(offer, available=2, soft_deleted=True)
        create_mediation(stock.offer)

        repository.save(user, stock)

        DiscoveryView.refresh(concurrently=False)

        # When
        offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

        # Then
        assert len(offers) == 0

    @clean_database
    def test_should_not_return_offers_from_non_validated_venue(self, app):
        # Given
        product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34', longitude=2.295695,
                             latitude=49.894171, validation_token='nimportequoi')
        offer = create_offer_with_thing_product(venue=venue, product=product)
        stock = create_stock_from_offer(offer, available=2)
        create_mediation(stock.offer)

        repository.save(user, stock)

        DiscoveryView.refresh(concurrently=False)

        # When
        offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

        # Then
        assert len(offers) == 0

    @clean_database
    def test_should_not_return_offers_from_non_validated_offerers(self, app):
        # Given
        product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
        offerer = create_offerer(validation_token='nimportequoi')
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34', longitude=2.295695,
                             latitude=49.894171)
        offer = create_offer_with_thing_product(venue=venue, product=product)
        stock = create_stock_from_offer(offer, available=2)
        create_mediation(stock.offer)

        repository.save(user, stock)

        DiscoveryView.refresh(concurrently=False)

        # When
        offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

        # Then
        assert len(offers) == 0

    @clean_database
    def test_should_not_return_offers_having_only_stocks_with_past_booking_limit_date_time(self, app):
        # Given
        product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34', longitude=2.295695,
                             latitude=49.894171)
        offer = create_offer_with_thing_product(venue=venue, product=product)
        one_day_ago = datetime.utcnow() - timedelta(days=1)
        stock = create_stock_from_offer(offer, available=2, booking_limit_datetime=one_day_ago)
        create_mediation(stock.offer)

        repository.save(user, stock)

        DiscoveryView.refresh(concurrently=False)

        # When
        offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

        # Then
        assert len(offers) == 0

    @clean_database
    def test_should_not_return_offers_from_venue_outside_user_iris(self, app):
        # given
        offerer = create_offerer(siren='123456789')
        user = create_user()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer)
        create_mediation(stock.offer)

        polygon = POLYGON_TEST
        polygon2 = Polygon([(2.195693, 50), (2.195693, 48), (2.595697, 48), (2.595697, 50)])

        venue_location_iris = create_iris(polygon)
        user_location_iris = create_iris(polygon2)

        repository.save(user, stock)

        iris_venue = create_iris_venue(venue_location_iris, venue)
        repository.save(iris_venue)

        DiscoveryView.refresh(concurrently=False)

        # when
        offers = get_offers_for_recommendation_v3(user=user, user_iris_id=user_location_iris.id,
                                                  user_is_geolocated=True)

        # then
        assert offers == []

    @clean_database
    def test_should_return_offer_when_offer_is_national(self, app):
        # Given
        offerer = create_offerer(siren='123456789')
        user = create_user()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, is_national=True)
        stock = create_stock_from_offer(offer)
        create_mediation(stock.offer)

        polygon = POLYGON_TEST
        polygon2 = Polygon([(2.195693, 50), (2.195693, 48), (2.595697, 48), (2.595697, 50)])

        venue_location_iris = create_iris(polygon)
        user_location_iris = create_iris(polygon2)

        repository.save(user, stock)

        iris_venue = create_iris_venue(venue_location_iris, venue)
        repository.save(iris_venue)

        DiscoveryView.refresh(concurrently=False)

        # When
        offers = get_offers_for_recommendation_v3(user=user, user_iris_id=user_location_iris.id,
                                                  user_is_geolocated=True)

        # Then
        assert offers == [offer]

    @clean_database
    def test_should_return_offers_regardless_of_location_when_user_is_not_geolocated(self, app):
        # given
        offerer = create_offerer(siren='123456789')
        user = create_user()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer)
        create_mediation(stock.offer)

        repository.save(user, stock)

        DiscoveryView.refresh(concurrently=False)

        # when
        offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

        # then
        assert len(offers) == 1

    @clean_database
    def test_should_return_only_national_offers_when_user_is_geolocated_outside_iris(self, app):
        # given
        offerer = create_offerer(siren='123456789')
        user = create_user()
        venue = create_venue(offerer)
        virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
        offer = create_offer_with_thing_product(venue)
        digital_offer = create_offer_with_thing_product(virtual_venue, thing_type=ThingType.MUSIQUE, url='https://url.com', is_national=True)
        national_offer = create_offer_with_thing_product(venue, is_national=True)
        stock = create_stock_from_offer(offer)
        stock_on_digital_offer = create_stock_from_offer(digital_offer)
        stock_on_national_offer = create_stock_from_offer(national_offer)
        create_mediation(offer)
        create_mediation(digital_offer)
        create_mediation(national_offer)

        repository.save(user, stock, stock_on_digital_offer, stock_on_national_offer)

        DiscoveryView.refresh(concurrently=False)

        # when
        offers = get_offers_for_recommendation_v3(user=user, user_iris_id=None, user_is_geolocated=True)

        # then
        assert len(offers) == 2
        assert digital_offer in offers
        assert national_offer in offers
