from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pytest

from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_criterion
from pcapi.model_creators.generic_creators import create_favorite
from pcapi.model_creators.generic_creators import create_mediation
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_seen_offer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_product_with_thing_type
from pcapi.model_creators.specific_creators import create_stock_from_offer
from pcapi.model_creators.specific_creators import create_stock_with_thing_offer
from pcapi.models.db import db
from pcapi.models.offer_type import EventType
from pcapi.models.offer_type import ThingType
from pcapi.repository import discovery_view_queries
from pcapi.repository import repository
from pcapi.repository.discovery_view_queries import order_by_digital_offers
from pcapi.repository.offer_queries import get_offers_for_recommendation


class GetOfferForRecommendationsTest:
    class FiltersTest:
        @pytest.mark.usefixtures("db_session")
        def test_when_department_code_00_should_return_offers_of_all_departements(self, app):
            # Given
            offerer = create_offerer(siren="123456789")
            user = create_user()
            venue_34 = create_venue(offerer, postal_code="34000", departement_code="34", siret=offerer.siren + "11111")
            venue_93 = create_venue(offerer, postal_code="93000", departement_code="93", siret=offerer.siren + "22222")
            venue_75 = create_venue(offerer, postal_code="75000", departement_code="75", siret=offerer.siren + "33333")
            offer_34 = create_offer_with_thing_product(venue_34)
            offer_93 = create_offer_with_thing_product(venue_93)
            offer_75 = create_offer_with_thing_product(venue_75)
            stock_34 = create_stock_from_offer(offer_34)
            stock_93 = create_stock_from_offer(offer_93)
            stock_75 = create_stock_from_offer(offer_75)
            create_mediation(stock_34.offer)
            create_mediation(stock_93.offer)
            create_mediation(stock_75.offer)

            repository.save(user, stock_34, stock_93, stock_75)

            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(user=user, departement_codes=["00"])

            # Then
            assert offer_34 in offers
            assert offer_93 in offers
            assert offer_75 in offers

        @pytest.mark.usefixtures("db_session")
        def test_should_return_offer_when_offer_is_national(self, app):
            # Given
            offerer = create_offerer(siren="123456789")
            user = create_user()
            venue_34 = create_venue(offerer, postal_code="34000", departement_code="34", siret=offerer.siren + "11111")
            offer_34 = create_offer_with_thing_product(venue_34)
            offer_national = create_offer_with_thing_product(venue_34, is_national=True)
            stock_34 = create_stock_from_offer(offer_34)
            stock_national = create_stock_from_offer(offer_national)
            create_mediation(stock_34.offer)
            create_mediation(stock_national.offer)

            repository.save(user, stock_34, stock_national)

            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(user=user, departement_codes=["93"])

            # Then
            assert offer_34 not in offers
            assert offer_national in offers

        @pytest.mark.usefixtures("db_session")
        def test_should_not_return_activation_event(self, app):
            # Given
            offerer = create_offerer(siren="123456789")
            user = create_user()
            venue_93 = create_venue(offerer, postal_code="93000", departement_code="93", siret=offerer.siren + "33333")
            offer_93 = create_offer_with_event_product(venue_93, thumb_count=1)
            offer_activation_93 = create_offer_with_event_product(
                venue_93, event_type=EventType.ACTIVATION, thumb_count=1
            )
            stock_93 = create_stock_from_offer(offer_93)
            stock_activation_93 = create_stock_from_offer(offer_activation_93)
            mediation1 = create_mediation(stock_93.offer)
            mediation2 = create_mediation(stock_activation_93.offer)

            repository.save(user, stock_93, stock_activation_93, mediation1, mediation2)

            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(user=user, departement_codes=["00"])

            # Then
            assert offer_93 in offers
            assert offer_activation_93 not in offers

        @pytest.mark.usefixtures("db_session")
        def test_should_not_return_activation_thing(self, app):
            # Given
            offerer = create_offerer(siren="123456789")
            user = create_user()
            venue_93 = create_venue(offerer, postal_code="93000", departement_code="93", siret=offerer.siren + "33333")
            offer_93 = create_offer_with_thing_product(venue_93, thumb_count=1)
            offer_activation_93 = create_offer_with_thing_product(
                venue_93, thing_type=ThingType.ACTIVATION, thumb_count=1
            )
            stock_93 = create_stock_from_offer(offer_93)
            stock_activation_93 = create_stock_from_offer(offer_activation_93)
            create_mediation(stock_93.offer)
            create_mediation(stock_activation_93.offer)

            repository.save(user, stock_93, stock_activation_93)

            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(user=user, departement_codes=["00"])

            # Then
            assert offer_93 in offers
            assert offer_activation_93 not in offers

        @pytest.mark.usefixtures("db_session")
        def test_should_return_offers_with_stock(self, app):
            # Given
            product = create_product_with_thing_type(thing_name="Lire un livre", is_national=True)
            offerer = create_offerer()
            user = create_user()
            venue = create_venue(offerer, postal_code="34000", departement_code="34")
            offer = create_offer_with_thing_product(venue=venue, product=product)
            stock = create_stock_from_offer(offer, quantity=2)
            create_mediation(stock.offer)
            repository.save(user, stock)

            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(user=user, departement_codes=["00"])

            # Then
            assert len(offers) == 1

        @pytest.mark.usefixtures("db_session")
        def test_should_return_offers_with_mediation_only(self, app):
            # Given
            offerer = create_offerer()
            user = create_user()
            venue = create_venue(offerer, postal_code="34000", departement_code="34")
            stock1 = create_stock_with_thing_offer(offerer, venue, name="thing_with_mediation")
            stock2 = create_stock_with_thing_offer(offerer, venue, name="thing_without_mediation")
            create_mediation(stock1.offer)
            repository.save(user, stock1, stock2)

            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(user=user, departement_codes=["00"])

            # Then
            assert len(offers) == 1
            assert offers[0].name == "thing_with_mediation"

        @pytest.mark.usefixtures("db_session")
        def test_should_not_return_offers_with_no_stock(self, app):
            # Given
            product = create_product_with_thing_type(thing_name="Lire un livre", is_national=True)
            offerer = create_offerer()
            user = create_user()
            venue = create_venue(offerer, postal_code="34000", departement_code="34")
            offer = create_offer_with_thing_product(venue=venue, product=product)
            stock = create_stock_from_offer(offer, price=0, quantity=2)
            booking1 = create_booking(user=user, stock=stock, is_cancelled=True, quantity=2, venue=venue)
            booking2 = create_booking(user=user, stock=stock, quantity=2, venue=venue)
            create_mediation(stock.offer)
            repository.save(user, booking1, booking2)
            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(user=user, departement_codes=["00"])

            # Then
            assert len(offers) == 0

        @pytest.mark.usefixtures("db_session")
        def test_should_not_return_booked_offers(self, app):
            # Given
            offerer = create_offerer()
            venue = create_venue(offerer, postal_code="34000", departement_code="34")
            offer = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
            stock = create_stock_from_offer(offer, price=0)
            user = create_user()
            booking = create_booking(user=user, stock=stock)
            create_mediation(stock.offer)
            repository.save(user, booking)
            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(user=user, departement_codes=["00"])

            # Then
            assert offers == []

        @pytest.mark.usefixtures("db_session")
        def test_should_not_return_favorite_offers(self, app):
            # Given
            offerer = create_offerer()
            user = create_user()
            venue = create_venue(offerer, postal_code="34000", departement_code="34")

            offer = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
            stock = create_stock_from_offer(offer, price=0)
            mediation = create_mediation(stock.offer)
            favorite = create_favorite(mediation=mediation, offer=offer, user=user)

            repository.save(user, favorite)
            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(user=user, departement_codes=["00"])

            # Then
            assert offers == []

    class OrderTest:
        @pytest.mark.usefixtures("db_session")
        def test_should_order_offers_by_criterion_score_first(self, app):
            # Given
            offerer = create_offerer()
            user = create_user()
            venue = create_venue(offerer, postal_code="34000", departement_code="34")
            digital_offer = create_offer_with_thing_product(
                venue=venue, is_national=True, thing_type=ThingType.LIVRE_EDITION, url="https://url.com"
            )
            physical_offer = create_offer_with_thing_product(
                venue=venue, is_national=True, thing_type=ThingType.LIVRE_EDITION, url=None
            )
            stock_digital_offer = create_stock_from_offer(digital_offer, quantity=2)
            stock_physical_offer = create_stock_from_offer(physical_offer, quantity=2)
            create_mediation(physical_offer)
            create_mediation(digital_offer)
            negative_criterion = create_criterion(name="negative", score_delta=-1)
            digital_offer.criteria = [negative_criterion]
            physical_offer.criteria = [negative_criterion, create_criterion(name="positive", score_delta=1)]

            repository.save(user, stock_digital_offer, stock_physical_offer)

            discovery_view_queries.create(db.session, order_by_digital_offers)
            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(user=user, departement_codes=["00"])

            # Then
            assert offers == [physical_offer, digital_offer]

        @pytest.mark.usefixtures("db_session")
        @patch("pcapi.repository.offer_queries.feature_queries.is_active", return_value=True)
        def test_should_return_ordered_offers_by_dateSeen_when_feature_is_active(self, app):
            # Given
            offerer = create_offerer()
            user = create_user()
            venue = create_venue(offerer, postal_code="34000", departement_code="34")
            offer_1 = create_offer_with_thing_product(
                venue=venue, is_national=True, thing_type=ThingType.LIVRE_EDITION, url="https://url.com"
            )
            offer_2 = create_offer_with_thing_product(
                venue=venue, is_national=True, thing_type=ThingType.LIVRE_EDITION, url=None
            )

            stock_digital_offer_1 = create_stock_from_offer(offer_1, quantity=2)
            stock_physical_offer_2 = create_stock_from_offer(offer_2, quantity=2)

            create_mediation(offer_1)
            create_mediation(offer_2)

            seen_offer_1 = create_seen_offer(offer_1, user, date_seen=datetime.utcnow() - timedelta(hours=12))
            seen_offer_2 = create_seen_offer(offer_2, user, date_seen=datetime.utcnow())

            repository.save(user, stock_digital_offer_1, stock_physical_offer_2, seen_offer_1, seen_offer_2)

            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(user=user, departement_codes=["00"])

            # Then
            assert offers == [offer_1, offer_2]

        @pytest.mark.usefixtures("db_session")
        @patch("pcapi.repository.offer_queries.feature_queries.is_active", return_value=True)
        def test_should_return_unseen_offers_first_for_specific_beneficiary_when_feature_is_active(self, app):
            # Given
            offerer = create_offerer()
            user_1 = create_user(email="beneficiary1@example.com")
            user_2 = create_user(email="beneficiary2@example.com")

            venue = create_venue(offerer, postal_code="34000", departement_code="34")
            offer_1 = create_offer_with_thing_product(
                venue=venue, is_national=True, thing_type=ThingType.LIVRE_EDITION, url=None
            )
            offer_2 = create_offer_with_thing_product(
                venue=venue, is_national=True, thing_type=ThingType.LIVRE_EDITION, url="https://url.com"
            )

            stock_digital_offer_1 = create_stock_from_offer(offer_1, quantity=2)
            stock_physical_offer_2 = create_stock_from_offer(offer_2, quantity=2)

            create_mediation(offer_1)
            create_mediation(offer_2)

            seen_offer_1 = create_seen_offer(offer_1, user_1, date_seen=datetime(2020, 1, 1))
            seen_offer_2 = create_seen_offer(offer_2, user_2, date_seen=datetime(2020, 2, 2))

            repository.save(user_1, user_2, stock_digital_offer_1, stock_physical_offer_2, seen_offer_1, seen_offer_2)

            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(user=user_1, departement_codes=["00"], limit=1)

            # Then
            assert offers == [offer_2]

        @pytest.mark.usefixtures("db_session")
        @patch("pcapi.repository.offer_queries.feature_queries.is_active", return_value=False)
        @patch("pcapi.repository.offer_queries.order_offers_by_unseen_offers_first")
        def test_should_not_order_offers_by_dateSeen_when_feature_is_not_active(
            self, mock_order_offers_by_unseen_offers_first, app
        ):
            # Given
            offerer = create_offerer()
            user = create_user()
            venue = create_venue(offerer, postal_code="34000", departement_code="34")
            offer = create_offer_with_thing_product(venue=venue, is_national=True, thing_type=ThingType.LIVRE_EDITION)

            stock_offer = create_stock_from_offer(offer, quantity=2)

            create_mediation(offer)

            repository.save(user, stock_offer)

            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(user=user, departement_codes=["00"])
            # Then
            mock_order_offers_by_unseen_offers_first.assert_not_called()
