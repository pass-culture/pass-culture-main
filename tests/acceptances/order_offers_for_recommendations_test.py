from models.db import db
from models.offer_type import ThingType
from repository import repository, discovery_view_queries
from repository.offer_queries import get_offers_for_recommendation
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_criterion, \
    create_user, create_offerer, create_venue, \
    create_mediation
from tests.model_creators.specific_creators import create_stock_from_offer, \
    create_offer_with_thing_product


@clean_database
def test_putting_a_super_bonus_to_a_physical_offer_puts_it_on_top_of_recommended_offers(app):
    # Given
    offerer = create_offerer()
    user = create_user()
    venue = create_venue(offerer, postal_code='34000',
                         departement_code='34')
    digital_offer_with_bonus = create_offer_with_thing_product(venue=venue, is_national=True,
                                                               thing_type=ThingType.LIVRE_EDITION,
                                                               url='https://url.com')
    digital_offer_with_bonus.criteria = [create_criterion(name='negative', score_delta=1)]

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
    physical_offer_with_super_bonus.criteria = [create_criterion(name='negative', score_delta=2)]

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
    offers = get_offers_for_recommendation(departement_codes=['00'],
                                           user=user)

    # Then
    assert offers == [physical_offer_with_super_bonus, digital_offer_with_bonus, digital_offer, physical_offer,
                      digital_offer_with_malus]


@clean_database
def test_updating_offers_order_should_change_order_in_materialized_view():
    # Given
    offerer = create_offerer()
    user = create_user()
    venue = create_venue(offerer, postal_code='34000',
                         departement_code='34')
    digital_offer_with_bonus = create_offer_with_thing_product(venue=venue, is_national=True,
                                                               thing_type=ThingType.LIVRE_EDITION,
                                                               url='https://url.com')
    digital_offer_with_bonus.criteria = [create_criterion(name='negative', score_delta=1)]

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
    physical_offer_with_super_bonus.criteria = [create_criterion(name='negative', score_delta=2)]

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
    old_ordered_offers = get_offers_for_recommendation(departement_codes=['00'],
                                                       user=user)

    def order_by_digital_offers_test() -> str:
        return f"""
                    ROW_NUMBER() OVER (
                        ORDER BY offer.url IS NOT NULL DESC,
                        (
                            SELECT COALESCE(SUM(criterion."scoreDelta"), 0) AS coalesce_1
                            FROM criterion, offer_criterion
                            WHERE criterion.id = offer_criterion."criterionId"
                                AND offer_criterion."offerId" = offer.id
                        ) DESC
                    )
                """

    discovery_view_queries.update(db.session, order_by_digital_offers_test)
    discovery_view_queries.refresh(concurrently=False)

    # When
    new_ordered_offers = get_offers_for_recommendation(departement_codes=['00'],
                                                       user=user)

    # Check
    assert old_ordered_offers == [physical_offer_with_super_bonus, digital_offer_with_bonus, digital_offer, physical_offer,
                                  digital_offer_with_malus]
    assert new_ordered_offers == [digital_offer_with_bonus, digital_offer, digital_offer_with_malus,
                                  physical_offer_with_super_bonus, physical_offer]
