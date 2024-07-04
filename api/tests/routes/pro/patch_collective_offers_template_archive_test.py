from unittest.mock import patch

import pytest

from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.educational.models import CollectiveOfferTemplate
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import assert_num_queries


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def when_archiving_existing_offers_templates(self, client):
        # Given
        offer1 = CollectiveOfferTemplateFactory()
        venue = offer1.venue
        offer2 = CollectiveOfferTemplateFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)
        client = client.with_session_auth("pro@example.com")

        # When
        data = {"ids": [offer1.id, offer2.id]}

        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            # 1. authentication
            # 2. load current_user
            # 3. retrieve all collective_order.ids to batch them in pool for update
            # 4. update dateArchive on collective_offer
            with assert_num_queries(4):
                response = client.patch("/collective/offers-template/archive", json=data)

        # Then
        assert response.status_code == 204
        assert CollectiveOfferTemplate.query.get(offer1.id).isArchived
        assert CollectiveOfferTemplate.query.get(offer2.id).isArchived

    def when_archiving_existing_offers_from_other_offerer(self, client):
        # Given
        offer = CollectiveOfferTemplateFactory()
        venue = offer.venue
        offerer = venue.managingOfferer

        other_offer = CollectiveOfferTemplateFactory()
        other_venue = other_offer.venue
        other_offerer = other_venue.managingOfferer

        # Ensure that the offerer is different
        assert other_offerer.id != offerer.id

        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)
        client = client.with_session_auth("pro@example.com")

        # When
        data = {"ids": [offer.id, other_offer.id]}

        response = client.patch("/collective/offers-template/archive", json=data)

        # Then
        assert response.status_code == 204
        assert CollectiveOfferTemplate.query.get(offer.id).isArchived
        assert not CollectiveOfferTemplate.query.get(other_offer.id).isArchived
