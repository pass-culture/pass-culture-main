import pytest

from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_product_with_thing_subcategory
from pcapi.repository import repository
from pcapi.repository.offer_queries import get_offers_by_ids
from pcapi.repository.offer_queries import get_offers_by_venue_id
from pcapi.repository.offer_queries import get_paginated_active_offer_ids
from pcapi.repository.offer_queries import get_paginated_offer_ids_by_venue_id


class FindOffersTest:
    @pytest.mark.usefixtures("db_session")
    def test_get_offers_by_venue_id_returns_offers_matching_venue_id(self, app):
        # Given
        product = create_product_with_thing_subcategory(thing_name="Lire un livre", is_national=True)
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code="34000", departement_code="34")
        offer = create_offer_with_thing_product(venue=venue, product=product)
        repository.save(offer)

        # When
        offers = get_offers_by_venue_id(venue.id)

        # Then
        assert len(offers) == 1
        assert offers[0].venueId == venue.id


class GetOffersByIdsTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_all_existing_offers_when_offer_ids_are_given(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_thing_product(venue=venue)
        offer2 = create_offer_with_thing_product(venue=venue)
        repository.save(offer1, offer2)
        offer_ids = [0, offer1.id, offer2.id]

        # When
        offers = get_offers_by_ids(offer_ids)

        # Then
        assert len(offers) == 2
        assert offer1 in offers
        assert offer2 in offers


class GetPaginatedActiveOfferIdsTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_two_offer_ids_from_first_page_when_limit_is_two_and_two_active_offers(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(is_active=True, venue=venue)
        offer2 = create_offer_with_event_product(is_active=True, venue=venue)
        create_offer_with_thing_product(is_active=True, venue=venue)
        create_offer_with_thing_product(is_active=True, venue=venue)
        repository.save(offer1, offer2)

        # When
        offer_ids = get_paginated_active_offer_ids(limit=2, page=0)

        # Then
        assert set(offer_ids) == {offer1.id, offer2.id}

    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_offer_id_from_second_page_when_limit_is_1_and_three_active_offers(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(is_active=True, venue=venue)
        offer2 = create_offer_with_event_product(is_active=False, venue=venue)
        offer3 = create_offer_with_thing_product(is_active=True, venue=venue)
        create_offer_with_thing_product(is_active=True, venue=venue)
        repository.save(offer1, offer2)

        # When
        offer_ids = get_paginated_active_offer_ids(limit=1, page=1)

        # Then
        assert offer_ids == [offer3.id]

    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_offer_id_from_third_page_when_limit_is_1_and_three_active_offers(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(is_active=True, venue=venue)
        offer2 = create_offer_with_event_product(is_active=False, venue=venue)
        create_offer_with_thing_product(is_active=True, venue=venue)
        offer4 = create_offer_with_thing_product(is_active=True, venue=venue)
        repository.save(offer1, offer2)

        # When
        offer_ids = get_paginated_active_offer_ids(limit=1, page=2)

        # Then
        assert offer_ids == [offer4.id]


class GetPaginatedOfferIdsByVenueIdTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_offer_id_in_two_offers_from_first_page_when_limit_is_one(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(venue=venue)
        offer2 = create_offer_with_event_product(venue=venue)
        repository.save(offer1, offer2)

        # When
        offer_ids = get_paginated_offer_ids_by_venue_id(venue_id=venue.id, limit=1, page=0)

        # Then
        assert offer_ids == [offer1.id]

    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_offer_id_in_two_offers_from_second_page_when_limit_is_one(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(venue=venue)
        offer2 = create_offer_with_event_product(venue=venue)
        repository.save(offer1, offer2)

        # When
        offer_ids = get_paginated_offer_ids_by_venue_id(venue_id=venue.id, limit=1, page=1)

        # Then
        assert offer_ids == [offer2.id]
