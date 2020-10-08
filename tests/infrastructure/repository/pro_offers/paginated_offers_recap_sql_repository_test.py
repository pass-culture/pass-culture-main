import pytest
from pcapi.model_creators.generic_creators import create_offerer, create_user, create_user_offerer, create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product, create_offer_with_thing_product, create_product_with_event_type, create_product_with_thing_type

from pcapi.domain.identifier.identifier import Identifier
from pcapi.domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap
from pcapi.infrastructure.repository.pro_offers.paginated_offers_recap_sql_repository import PaginatedOffersSQLRepository
from pcapi.repository import repository


class PaginatedOfferSQLRepositoryTest:
    @pytest.mark.usefixtures("db_session")
    def should_return_paginated_offers_with_details_of_pagination_and_offers_of_requested_page(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        offer2 = create_offer_with_thing_product(venue)
        repository.save(user_offerer, offer1, offer2)
        requested_page = 2
        requested_offers_per_page = 1

        # When
        paginated_offers = PaginatedOffersSQLRepository().get_paginated_offers_for_offerer_venue_and_keywords(
                user_id=user.id,
                user_is_admin=user.isAdmin,
                offers_per_page=requested_offers_per_page,
                page=requested_page
        )

        # Then
        assert isinstance(paginated_offers, PaginatedOffersRecap)
        assert paginated_offers.total_offers == 2
        assert paginated_offers.current_page == requested_page
        assert paginated_offers.total_pages == 2
        assert len(paginated_offers.offers) == 1
        assert paginated_offers.offers[0].identifier == Identifier(offer1.id)

    @pytest.mark.usefixtures("db_session")
    def should_return_a_number_of_page_as_an_integer(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        offer2 = create_offer_with_thing_product(venue)
        offer3 = create_offer_with_thing_product(venue)
        repository.save(user_offerer, offer1, offer2, offer3)
        requested_page = 1
        requested_offers_per_page = 2

        # When
        paginated_offers = PaginatedOffersSQLRepository().get_paginated_offers_for_offerer_venue_and_keywords(
                user_id=user.id,
                user_is_admin=user.isAdmin,
                offers_per_page=requested_offers_per_page,
                page=requested_page
        )

        # Then
        assert isinstance(paginated_offers, PaginatedOffersRecap)
        assert paginated_offers.total_pages == 2

    @pytest.mark.usefixtures("db_session")
    def should_return_offers_sorted_by_id_desc(self, app):
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
                offers_per_page=10
        )

        # Then
        assert paginated_offers.offers[0].identifier.persisted > paginated_offers.offers[1].identifier.persisted

    @pytest.mark.usefixtures("db_session")
    def should_return_offers_of_given_venue(self, app):
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
            venue_id=Identifier(requested_venue.id),
            page=1,
            offers_per_page=10
        )

        # then
        offers_id = [offer.identifier for offer in paginated_offers.offers]
        assert Identifier(offer_on_requested_venue.id) in offers_id
        assert Identifier(offer_on_other_venue.id) not in offers_id

    @pytest.mark.usefixtures("db_session")
    def should_return_offers_matching_searched_name(self, app):
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
            name_keywords='Jac rencon',
            page=1,
            offers_per_page=10
        )

        # then
        offers_id = [offer.identifier for offer in paginated_offers.offers]
        assert Identifier(offer_matching_requested_name.id) in offers_id
        assert Identifier(offer_not_matching_requested_name.id) not in offers_id
