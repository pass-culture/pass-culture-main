from datetime import datetime, timedelta
from unittest.mock import patch

from models.db import db
from models.offer_type import ThingType
from repository import repository, discovery_view_queries, discovery_view_v3_queries
from repository.discovery_view_queries import _order_by_digital_offers
from repository.offer_queries import get_offers_for_recommendation, get_offers_for_recommendation_v3
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_criterion, \
    create_user, create_offerer, create_venue, \
    create_mediation, create_seen_offer
from tests.model_creators.specific_creators import create_stock_from_offer, \
    create_offer_with_thing_product


class DiscoveryViewTest:
    @clean_database
    @patch('repository.offer_queries.feature_queries.is_active', return_value=False)
    def test_putting_a_super_bonus_to_a_physical_offer_puts_it_on_top_of_recommended_offers_when_feature_is_not_active(
            self,
            mock_feature_save_seen_offers_enabled,
            app):
        # Given
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000',
                             departement_code='34')

        physical_offer_with_super_bonus = create_offer_with_thing_product(thing_name="Physical with highest bonus",
                                                                          venue=venue, is_national=True,
                                                                          thing_type=ThingType.LIVRE_EDITION,
                                                                          url=None)
        digital_offer_with_bonus = create_offer_with_thing_product(thing_name="Digital offer with bonus",
                                                                   venue=venue, is_national=True,
                                                                   thing_type=ThingType.LIVRE_EDITION,
                                                                   url='https://url.com')
        digital_offer = create_offer_with_thing_product(thing_name="Digital offer without bonus",
                                                        venue=venue, is_national=True,
                                                        thing_type=ThingType.LIVRE_EDITION, url='https://url.com')
        digital_offer_with_malus = create_offer_with_thing_product(thing_name="Digital offer with malus",
                                                                   venue=venue, is_national=True,
                                                                   thing_type=ThingType.LIVRE_EDITION,
                                                                   url='https://url.com')
        physical_offer = create_offer_with_thing_product(thing_name="Physical offer without bonus/malus", venue=venue,
                                                         is_national=True,
                                                         thing_type=ThingType.LIVRE_EDITION, url=None)

        digital_offer_with_bonus.criteria = [create_criterion(name='positive', score_delta=1)]
        digital_offer_with_malus.criteria = [create_criterion(name='negative', score_delta=-1)]
        physical_offer_with_super_bonus.criteria = [create_criterion(name='positive_value_2', score_delta=2)]

        stock_digital_offer_with_bonus = create_stock_from_offer(digital_offer_with_bonus, quantity=2)
        stock_digital_offer = create_stock_from_offer(digital_offer, quantity=2)
        stock_digital_offer_with_malus = create_stock_from_offer(digital_offer_with_malus, quantity=2)
        stock_physical_offer = create_stock_from_offer(physical_offer, quantity=2)
        stock_physical_offer_with_super_bonus = create_stock_from_offer(physical_offer_with_super_bonus, quantity=2)

        create_mediation(digital_offer_with_bonus)
        create_mediation(digital_offer)
        create_mediation(digital_offer_with_malus)
        create_mediation(physical_offer)
        create_mediation(physical_offer_with_super_bonus)

        repository.save(user, stock_digital_offer_with_bonus, stock_digital_offer, stock_digital_offer_with_malus,
                        stock_physical_offer, stock_physical_offer_with_super_bonus)

        discovery_view_queries.refresh(concurrently=False)

        # When
        offers = get_offers_for_recommendation(user=user, departement_codes=['00'])

        # Then
        assert len(offers) == 5
        assert offers[0].offer == physical_offer_with_super_bonus
        assert offers[1].offer == digital_offer_with_bonus
        assert offers[2].offer == digital_offer
        assert offers[3].offer == physical_offer
        assert offers[4].offer == digital_offer_with_malus

    @clean_database
    @patch('repository.offer_queries.feature_queries.is_active', return_value=True)
    def test_return_ordered_offers_by_digital_and_score_and_dateSeen_criterias_when_feature_is_active(self,
                                                                                                      mock_feature_save_seen_offers_enabled,
                                                                                                      app):
        # Given
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000',
                             departement_code='34')
        digital_offer_with_bonus = create_offer_with_thing_product(venue=venue, is_national=True,
                                                                   thing_type=ThingType.LIVRE_EDITION,
                                                                   url='https://url.com')
        digital_offer_with_bonus.criteria = [create_criterion(name='positive', score_delta=1)]

        digital_offer = create_offer_with_thing_product(venue=venue, is_national=True,
                                                        thing_type=ThingType.LIVRE_EDITION, url='https://url.com')
        digital_offer_with_malus = create_offer_with_thing_product(venue=venue, is_national=True,
                                                                   thing_type=ThingType.LIVRE_EDITION,
                                                                   url='https://url.com')
        digital_offer_with_malus.criteria = [create_criterion(name='negative', score_delta=-1)]
        physical_offer = create_offer_with_thing_product(venue=venue, is_national=True,
                                                         thing_type=ThingType.LIVRE_EDITION, url=None)
        physical_offer_with_super_bonus = create_offer_with_thing_product(venue=venue, is_national=True,
                                                                          thing_type=ThingType.LIVRE_EDITION,
                                                                          url=None)
        physical_offer_with_super_bonus.criteria = [create_criterion(name='super_positive', score_delta=2)]

        stock_digital_offer_with_bonus = create_stock_from_offer(digital_offer_with_bonus, quantity=2)
        stock_digital_offer = create_stock_from_offer(digital_offer, quantity=2)
        stock_digital_offer_with_malus = create_stock_from_offer(digital_offer_with_malus, quantity=2)
        stock_physical_offer = create_stock_from_offer(physical_offer, quantity=2)
        stock_physical_offer_with_super_bonus = create_stock_from_offer(physical_offer_with_super_bonus, quantity=2)

        create_mediation(digital_offer_with_bonus)
        create_mediation(digital_offer)
        create_mediation(digital_offer_with_malus)
        create_mediation(physical_offer)
        create_mediation(physical_offer_with_super_bonus)

        seen_digital_offer = create_seen_offer(digital_offer, user, date_seen=datetime.utcnow())
        seen_digital_offer_with_malus = create_seen_offer(digital_offer_with_malus, user,
                                                          date_seen=datetime.utcnow() - timedelta(hours=12))

        repository.save(user, stock_digital_offer_with_bonus, stock_digital_offer, stock_digital_offer_with_malus,
                        stock_physical_offer, stock_physical_offer_with_super_bonus,
                        seen_digital_offer, seen_digital_offer_with_malus)

        discovery_view_queries.create(db.session, _order_by_digital_offers)
        discovery_view_queries.refresh(concurrently=False)

        # When
        offers = get_offers_for_recommendation(user=user, departement_codes=['00'])

        # Then
        assert offers == [physical_offer_with_super_bonus, digital_offer_with_bonus, physical_offer,
                          digital_offer_with_malus, digital_offer]
