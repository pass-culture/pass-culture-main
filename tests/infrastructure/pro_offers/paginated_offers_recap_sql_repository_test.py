from domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap
from infrastructure.repository.pro_offers.paginated_offers_recap_sql_repository import PaginatedOffersSQLRepository
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
        assert isinstance(paginated_offers, PaginatedOffersRecap)
        assert paginated_offers.total == 2
        assert len(paginated_offers.offers) == 1
        assert paginated_offers.offers[0].identifier == offer1.id

    @clean_database
    def test_return_offers_sorted_by_id_desc(self, app):
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
        assert paginated_offers.offers[0].identifier > paginated_offers.offers[1].identifier

    @clean_database
    def test_return_offers_of_given_venue(self, app):
        user = create_user()
        offerer = create_offerer(siren='123456789')
        user_offerer = create_user_offerer(user=user, offerer=offerer)

        product_event = create_product_with_event_type(event_name='Rencontre avec Jacques Martin')
        product_thing = create_product_with_thing_type(thing_name='Belle du Seigneur')
        requested_venue = create_venue(offerer=offerer, name='Bataclan', city='Paris', siret=offerer.siren + '12345')
        other_venue = create_venue(offerer=offerer, name='Librairie la Rencontre', city='Saint Denis', siret=offerer.siren + '54321')
        offer_on_requested_venue = create_offer_with_event_product(venue=requested_venue, product=product_event)
        offer_on_other_venue = create_offer_with_thing_product(venue=other_venue, product=product_thing)
        repository.save(
                user_offerer, offer_on_requested_venue, offer_on_other_venue
        )

        # when
        paginated_offers = PaginatedOffersSQLRepository().get_paginated_offers_for_offerer_venue_and_keywords(
                user_id=user.id,
                user_is_admin=user.isAdmin,
                venue_id=requested_venue.id,
                page=1,
                pagination_limit=10
        )

        # then
        offers_id = [offer.identifier for offer in paginated_offers.offers]
        assert offer_on_requested_venue.id in offers_id
        assert offer_on_other_venue.id not in offers_id

    @clean_database
    def test_return_offers_matching_searched_name(self, app):
        user = create_user()
        offerer = create_offerer(siren='123456789')
        user_offerer = create_user_offerer(user=user, offerer=offerer)

        product_event = create_product_with_event_type(event_name='Rencontre avec Jacques Martin')
        product_thing = create_product_with_thing_type(thing_name='Belle du Seigneur', author_name='Jacqueline Rencon')
        requested_venue = create_venue(offerer=offerer, name='Bataclan', city='Paris', siret=offerer.siren + '12345')
        other_venue = create_venue(offerer=offerer, name='Librairie la Rencontre des jachères', city='Saint Denis', siret=offerer.siren + '54321')
        offer_matching_requested_name = create_offer_with_event_product(venue=requested_venue, product=product_event)
        offer_not_matching_requested_name = create_offer_with_thing_product(venue=other_venue, product=product_thing)
        repository.save(
                user_offerer, offer_matching_requested_name, offer_not_matching_requested_name
        )

        # when
        paginated_offers = PaginatedOffersSQLRepository().get_paginated_offers_for_offerer_venue_and_keywords(
                user_id=user.id,
                user_is_admin=user.isAdmin,
                keywords='Jac rencon',
                page=1,
                pagination_limit=10
        )

        # then
        offers_id = [offer.identifier for offer in paginated_offers.offers]
        assert offer_matching_requested_name.id in offers_id
        assert offer_not_matching_requested_name.id not in offers_id
