from domain.pro_offers.paginated_offers import PaginatedOffers
from infrastructure.repository.pro_offers.paginated_offer_sql_repository import PaginatedOffersSQLRepository
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user, create_offerer, create_user_offerer, create_venue
from tests.model_creators.specific_creators import create_offer_with_thing_product
from tests.model_creators.specific_creators import create_product_with_event_type, create_product_with_thing_type, create_offer_with_event_product


class PaginatedOfferSQLRepositoryTest:
    @clean_database
    def test_should_return_paginated_offers_with_total_number_of_offers_and_offers_of_requested_page(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        offer2 = create_offer_with_thing_product(venue)
        repository.save(user_offerer, offer1, offer2)

        # When
        paginated_offers = PaginatedOffersSQLRepository().get_paginated_offers_for_offerer_venue_and_keywords(
                user_id=user.id,
                user_is_admin=user.isAdmin,
                pagination_limit=1,
                page=2
        )

        # Then
        assert isinstance(paginated_offers, PaginatedOffers)
        assert paginated_offers.total == 2
        assert len(paginated_offers.offers) == 1
        assert paginated_offers.offers[0].id == offer1.id

    @clean_database
    def test_returns_offers_sorted_by_id_desc(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        offer2 = create_offer_with_thing_product(venue)
        repository.save(user_offerer, offer1, offer2)

        # When
        paginated_offers = PaginatedOffersSQLRepository().get_paginated_offers_for_offerer_venue_and_keywords(
                user_id=user.id,
                user_is_admin=user.isAdmin,
                page=1,
                pagination_limit=10
        )

        # Then
        assert paginated_offers.offers[0].id > paginated_offers.offers[1].id

    @clean_database
    def test_find_offers_with_filter_parameters_with_partial_keywords_and_filter_by_venue(self, app):
        user = create_user()
        offerer1 = create_offerer(siren='123456789')
        offerer2 = create_offerer(siren='987654321')
        ko_offerer3 = create_offerer(siren='123456780')
        user_offerer1 = create_user_offerer(user=user, offerer=offerer1)
        user_offerer2 = create_user_offerer(user=user, offerer=offerer2)

        ok_product_event = create_product_with_event_type(event_name='Rencontre avec Jacques Martin')
        ok_product_thing = create_product_with_thing_type(thing_name='Rencontrez Jacques Chirac')
        event_product2 = create_product_with_event_type(event_name='Concert de contrebasse')
        thing1_product = create_product_with_thing_type(thing_name='Jacques la fripouille')
        thing2_product = create_product_with_thing_type(thing_name='Belle du Seigneur')
        offerer = create_offerer(siren='123456789')
        venue1 = create_venue(offerer=offerer1, name='Bataclan', city='Paris', siret=offerer.siren + '12345')
        venue2 = create_venue(offerer=offerer2, name='Librairie la Rencontre', city='Saint Denis',
                              siret=offerer.siren + '54321')
        ko_venue3 = create_venue(ko_offerer3, name='Une librairie du méchant concurrent gripsou', city='Saint Denis',
                                 siret=ko_offerer3.siren + '54321')
        ok_offer1 = create_offer_with_event_product(venue=venue1, product=ok_product_event)
        ok_offer2 = create_offer_with_thing_product(venue=venue1, product=ok_product_thing)
        ko_offer2 = create_offer_with_event_product(venue=venue1, product=event_product2)
        ko_offer3 = create_offer_with_thing_product(venue=ko_venue3, product=thing1_product)
        ko_offer4 = create_offer_with_thing_product(venue=venue2, product=thing2_product)
        repository.save(
                user_offerer1, user_offerer2, ko_offerer3,
                ok_offer1, ko_offer2, ko_offer3, ko_offer4
        )

        # when
        paginated_offers = PaginatedOffersSQLRepository().get_paginated_offers_for_offerer_venue_and_keywords(
                user_id=user.id,
                user_is_admin=user.isAdmin,
                venue_id=venue1.id,
                keywords='Jacq Rencon',
                page=1,
                pagination_limit=10
        )

        # then
        offers_id = [offer.id for offer in paginated_offers.offers]
        assert ok_offer1.id in offers_id
        assert ok_offer2.id in offers_id
        assert ko_offer2.id not in offers_id
        assert ko_offer3.id not in offers_id
        assert ko_offer4.id not in offers_id
