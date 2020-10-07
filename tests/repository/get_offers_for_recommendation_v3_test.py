from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from shapely.geometry import Polygon

from pcapi.models import EventType, ThingType
from pcapi.repository import repository, discovery_view_v3_queries
from pcapi.repository.offer_queries import get_offers_for_recommendation_v3
from pcapi.model_creators.generic_creators import create_booking, \
    create_criterion, \
    create_favorite, create_iris, \
    create_iris_venue, \
    create_mediation, \
    create_offerer, create_user, \
    create_venue, create_seen_offer
from pcapi.model_creators.specific_creators import \
    create_offer_with_event_product, create_offer_with_thing_product, \
    create_product_with_thing_type, create_stock_from_offer, \
    create_stock_with_thing_offer
from tests.test_utils import POLYGON_TEST


class GetOffersForRecommendationV3Test:
    class UniversalBehaviorTest:
        class FiltersTest:
            @pytest.mark.usefixtures("db_session")
            def test_filter_should_not_return_activation_event(self, app):
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

                discovery_view_v3_queries.refresh(concurrently=False)

                # When
                offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

                # Then
                assert offer in offers
                assert offer_activation not in offers

            @pytest.mark.usefixtures("db_session")
            def test_filter_should_not_return_activation_thing(self, app):
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

                discovery_view_v3_queries.refresh(concurrently=False)

                # When
                offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

                # Then
                assert offer_93 in offers
                assert offer_activation_93 not in offers

            @pytest.mark.usefixtures("db_session")
            def test_filter_should_return_offers_with_stock(self, app):
                # Given
                product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
                offerer = create_offerer()
                user = create_user()
                venue = create_venue(offerer, postal_code='34000', departement_code='34', longitude=2.295695,
                                     latitude=49.894171)
                offer = create_offer_with_thing_product(venue=venue, product=product)
                stock = create_stock_from_offer(offer, quantity=2)
                create_mediation(stock.offer)

                repository.save(user, stock)

                discovery_view_v3_queries.refresh(concurrently=False)

                # When
                offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

                # Then
                assert len(offers) == 1

            @pytest.mark.usefixtures("db_session")
            def test_filter_should_return_offers_with_mediation_only(self, app):
                # Given
                offerer = create_offerer()
                user = create_user()
                venue = create_venue(offerer, postal_code='34000', departement_code='34')
                stock1 = create_stock_with_thing_offer(offerer, venue, name='thing_with_mediation')
                stock2 = create_stock_with_thing_offer(offerer, venue, name='thing_without_mediation')
                create_mediation(stock1.offer)

                repository.save(user, stock1, stock2)
                discovery_view_v3_queries.refresh(concurrently=False)

                # When
                offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

                # Then
                assert len(offers) == 1
                assert offers[0].name == 'thing_with_mediation'

            @pytest.mark.usefixtures("db_session")
            def test_filter_should_not_return_offers_with_no_stock(self, app):
                # Given
                product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
                offerer = create_offerer()
                user = create_user()
                venue = create_venue(offerer, postal_code='34000', departement_code='34')
                offer = create_offer_with_thing_product(venue=venue, product=product)
                stock = create_stock_from_offer(offer, price=0, quantity=2)
                booking1 = create_booking(user=user, stock=stock, is_cancelled=True, quantity=2, venue=venue)
                booking2 = create_booking(user=user, stock=stock, quantity=2, venue=venue)
                create_mediation(stock.offer)

                repository.save(user, booking1, booking2)

                discovery_view_v3_queries.refresh(concurrently=False)

                # When
                offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

                # Then
                assert len(offers) == 0

            @pytest.mark.usefixtures("db_session")
            def test_filter_should_not_return_offers_having_only_soft_deleted_stocks(self, app):
                # Given
                product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
                offerer = create_offerer()
                user = create_user()
                venue = create_venue(offerer, postal_code='34000', departement_code='34', longitude=2.295695,
                                     latitude=49.894171)
                offer = create_offer_with_thing_product(venue=venue, product=product)
                stock = create_stock_from_offer(offer, quantity=2, soft_deleted=True)
                create_mediation(stock.offer)

                repository.save(user, stock)

                discovery_view_v3_queries.refresh(concurrently=False)

                # When
                offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

                # Then
                assert len(offers) == 0

            @pytest.mark.usefixtures("db_session")
            def test_filter_should_not_return_offers_from_non_validated_venue(self, app):
                # Given
                product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
                offerer = create_offerer()
                user = create_user()
                venue = create_venue(offerer, postal_code='34000', departement_code='34', longitude=2.295695,
                                     latitude=49.894171, validation_token='nimportequoi')
                offer = create_offer_with_thing_product(venue=venue, product=product)
                stock = create_stock_from_offer(offer, quantity=2)
                create_mediation(stock.offer)

                repository.save(user, stock)

                discovery_view_v3_queries.refresh(concurrently=False)

                # When
                offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

                # Then
                assert len(offers) == 0

            @pytest.mark.usefixtures("db_session")
            def test_filter_should_not_return_offers_from_non_validated_offerers(self, app):
                # Given
                product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
                offerer = create_offerer(validation_token='nimportequoi')
                user = create_user()
                venue = create_venue(offerer, postal_code='34000', departement_code='34', longitude=2.295695,
                                     latitude=49.894171)
                offer = create_offer_with_thing_product(venue=venue, product=product)
                stock = create_stock_from_offer(offer, quantity=2)
                create_mediation(stock.offer)

                repository.save(user, stock)

                discovery_view_v3_queries.refresh(concurrently=False)

                # When
                offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

                # Then
                assert len(offers) == 0

            @pytest.mark.usefixtures("db_session")
            def test_filter_should_not_return_offers_having_only_stocks_with_past_booking_limit_date_time(self, app):
                # Given
                product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
                offerer = create_offerer()
                user = create_user()
                venue = create_venue(offerer, postal_code='34000', departement_code='34', longitude=2.295695,
                                     latitude=49.894171)
                offer = create_offer_with_thing_product(venue=venue, product=product)
                one_day_ago = datetime.utcnow() - timedelta(days=1)
                stock = create_stock_from_offer(offer, quantity=2, booking_limit_datetime=one_day_ago)
                create_mediation(stock.offer)

                repository.save(user, stock)

                discovery_view_v3_queries.refresh(concurrently=False)

                # When
                offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

                # Then
                assert len(offers) == 0

        class OrderTest:
            @pytest.mark.usefixtures("db_session")
            def test_order_with_criteria_should_return_offer_with_highest_base_score_first(self, app):
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

                discovery_view_v3_queries.refresh(concurrently=False)

                # When
                offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False, limit=1)

                # Then
                assert offers[0].offer == offer2

            @pytest.mark.usefixtures("db_session")
            @patch('pcapi.repository.offer_queries.feature_queries.is_active', return_value=True)
            def test_order_should_return_ordered_offers_by_dateSeen_when_feature_is_active(self, app):
                # Given
                offerer = create_offerer()
                user = create_user()
                venue = create_venue(offerer, postal_code='34000',
                                     departement_code='34')
                offer_1 = create_offer_with_thing_product(venue=venue, is_national=True,
                                                          thing_type=ThingType.LIVRE_EDITION, url='https://url.com')
                offer_2 = create_offer_with_thing_product(venue=venue, is_national=True,
                                                          thing_type=ThingType.LIVRE_EDITION, url=None)

                stock_digital_offer_1 = create_stock_from_offer(offer_1, quantity=2)
                stock_physical_offer_2 = create_stock_from_offer(offer_2, quantity=2)

                create_mediation(offer_1)
                create_mediation(offer_2)

                seen_offer_1 = create_seen_offer(offer_1, user, date_seen=datetime.utcnow() - timedelta(hours=12))
                seen_offer_2 = create_seen_offer(offer_2, user, date_seen=datetime.utcnow())

                repository.save(user, stock_digital_offer_1, stock_physical_offer_2, seen_offer_1,
                                seen_offer_2)

                discovery_view_v3_queries.refresh(concurrently=False)

                # When
                offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

                # Then
                assert offers == [offer_1, offer_2]

            @pytest.mark.usefixtures("db_session")
            @patch('pcapi.repository.offer_queries.feature_queries.is_active', return_value=True)
            def test_order_should_return_unseen_offers_first_when_feature_is_active(self, app):
                # Given
                offerer = create_offerer()
                user = create_user()
                venue = create_venue(offerer, postal_code='34000',
                                     departement_code='34')
                offer_1 = create_offer_with_thing_product(venue=venue, is_national=True,
                                                          thing_type=ThingType.LIVRE_EDITION)
                offer_2 = create_offer_with_thing_product(venue=venue, is_national=True,
                                                          thing_type=ThingType.LIVRE_EDITION)
                offer_2.criteria = [create_criterion(name='positive', score_delta=1)]

                stock_digital_offer_1 = create_stock_from_offer(offer_1, quantity=2)
                stock_physical_offer_2 = create_stock_from_offer(offer_2, quantity=2)

                create_mediation(offer_1)
                create_mediation(offer_2)

                seen_offer = create_seen_offer(offer_2, user, date_seen=datetime.utcnow())

                repository.save(user, stock_digital_offer_1, stock_physical_offer_2, seen_offer)

                discovery_view_v3_queries.refresh(concurrently=False)

                # When
                offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False, limit=1)

                # Then
                assert offers[0] == offer_1

            @pytest.mark.usefixtures("db_session")
            @patch('pcapi.repository.offer_queries.feature_queries.is_active', return_value=False)
            @patch('pcapi.repository.offer_queries.order_offers_by_unseen_offers_first')
            def test_order_should_not_order_offers_by_dateSeen_when_feature_is_not_active(self, mock_order_offers_by_unseen_offers_first, app):
                # Given
                offerer = create_offerer()
                user = create_user()
                venue = create_venue(offerer, postal_code='34000', departement_code='34')
                offer = create_offer_with_thing_product(venue=venue, is_national=True, thing_type=ThingType.LIVRE_EDITION)

                stock_offer = create_stock_from_offer(offer, quantity=2)

                create_mediation(offer)

                repository.save(user, stock_offer)

                discovery_view_v3_queries.refresh(concurrently=False)

                # When
                offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

                # Then
                mock_order_offers_by_unseen_offers_first.assert_not_called()

    class UserSpecificBehaviorTest:
        @pytest.mark.usefixtures("db_session")
        def test_filter_should_not_return_booked_offers(self, app):
            # Given
            offerer = create_offerer()
            venue = create_venue(offerer, postal_code='34000', departement_code='34')
            offer = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
            stock = create_stock_from_offer(offer, price=0)
            user = create_user()
            booking = create_booking(user=user, stock=stock)
            create_mediation(stock.offer)

            repository.save(user, booking)

            discovery_view_v3_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

            # Then
            assert offers == []

        @pytest.mark.usefixtures("db_session")
        def test_filter_should_not_return_favorite_offers(self, app):
            # Given
            offerer = create_offerer()
            user = create_user()
            venue = create_venue(offerer, postal_code='34000', departement_code='34')

            offer = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
            stock = create_stock_from_offer(offer, price=0)
            mediation = create_mediation(stock.offer)
            favorite = create_favorite(mediation=mediation, offer=offer, user=user)

            repository.save(user, favorite)

            discovery_view_v3_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

            # Then
            assert offers == []

        class WhenUserIsGeolocatedTest:

            @pytest.mark.usefixtures("db_session")
            def test_filter_should_return_offer_when_offer_is_national(self, app):
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

                discovery_view_v3_queries.refresh(concurrently=False)

                # When
                offers = get_offers_for_recommendation_v3(user=user, user_iris_id=user_location_iris.id,
                                                          user_is_geolocated=True)

                # Then
                assert offers == [offer]

            @pytest.mark.usefixtures("db_session")
            def test_filter_should_not_return_offers_from_venue_outside_user_iris(self, app):
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

                discovery_view_v3_queries.refresh(concurrently=False)

                # when
                offers = get_offers_for_recommendation_v3(user=user, user_iris_id=user_location_iris.id,
                                                          user_is_geolocated=True)

                # then
                assert offers == []

            @pytest.mark.usefixtures("db_session")
            def test_filter_should_return_only_national_offers_when_user_is_geolocated_abroad(self, app):
                # given
                offerer = create_offerer(siren='123456789')
                user = create_user()
                venue = create_venue(offerer)
                virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
                offer = create_offer_with_thing_product(venue)
                digital_offer = create_offer_with_thing_product(virtual_venue, thing_type=ThingType.MUSIQUE,
                                                                url='https://url.com', is_national=True)
                national_offer = create_offer_with_thing_product(venue, is_national=True)
                stock = create_stock_from_offer(offer)
                stock_on_digital_offer = create_stock_from_offer(digital_offer)
                stock_on_national_offer = create_stock_from_offer(national_offer)
                create_mediation(offer)
                create_mediation(digital_offer)
                create_mediation(national_offer)

                repository.save(user, stock, stock_on_digital_offer, stock_on_national_offer)

                discovery_view_v3_queries.refresh(concurrently=False)

                # when
                offers = get_offers_for_recommendation_v3(user=user, user_iris_id=None, user_is_geolocated=True)

                # then
                assert len(offers) == 2
                assert digital_offer in offers
                assert national_offer in offers

        class WhenUserIsNotGeolocatedTest:

            @pytest.mark.usefixtures("db_session")
            def test_filter_should_return_offers_regardless_of_location(self, app):
                # given
                offerer = create_offerer(siren='123456789')
                user = create_user()
                venue = create_venue(offerer)
                offer = create_offer_with_thing_product(venue)
                stock = create_stock_from_offer(offer)
                create_mediation(stock.offer)

                repository.save(user, stock)

                discovery_view_v3_queries.refresh(concurrently=False)

                # when
                offers = get_offers_for_recommendation_v3(user=user, user_is_geolocated=False)

                # then
                assert len(offers) == 1
