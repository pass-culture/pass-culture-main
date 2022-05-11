import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.repository.offer_queries import get_paginated_active_offer_ids
from pcapi.repository.offer_queries import get_paginated_offer_ids_by_venue_id


pytestmark = pytest.mark.usefixtures("db_session")


class GetPaginatedActiveOfferIdsTest:
    def test_limit_and_page_arguments(self):
        venue = offerers_factories.VenueFactory()
        offer1 = offers_factories.OfferFactory(venue=venue)
        offer2 = offers_factories.OfferFactory(venue=venue)
        offer3 = offers_factories.OfferFactory(venue=venue)

        assert get_paginated_active_offer_ids(limit=2, page=0) == [offer1.id, offer2.id]
        assert get_paginated_active_offer_ids(limit=2, page=1) == [offer3.id]

    def test_exclude_inactive_offers(self):
        venue = offerers_factories.VenueFactory()
        offer1 = offers_factories.OfferFactory(venue=venue, isActive=True)
        _offer2 = offers_factories.OfferFactory(venue=venue, isActive=False)

        assert get_paginated_active_offer_ids(limit=2, page=0) == [offer1.id]


class GetPaginatedOfferIdsByVenueIdTest:
    def test_limit_and_page_arguments(self):
        venue1 = offerers_factories.VenueFactory()
        offer1 = offers_factories.OfferFactory(venue=venue1)
        offer2 = offers_factories.OfferFactory(venue=venue1)
        offer3 = offers_factories.OfferFactory(venue=venue1)
        _other_venue_offer = offers_factories.OfferFactory()

        assert get_paginated_offer_ids_by_venue_id(venue1.id, limit=2, page=0) == [offer1.id, offer2.id]
        assert get_paginated_offer_ids_by_venue_id(venue1.id, limit=2, page=1) == [offer3.id]

    def test_include_inactive_offers(self):
        venue = offerers_factories.VenueFactory()
        offer1 = offers_factories.OfferFactory(venue=venue, isActive=True)
        offer2 = offers_factories.OfferFactory(venue=venue, isActive=False)

        assert get_paginated_offer_ids_by_venue_id(venue.id, limit=2, page=0) == [offer1.id, offer2.id]
