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
            # 1. # authentication
            # 2. # load current_user
            # 3. # retrieve all offerer_ids relative to offer provided
            # 4. # retrieve all collective_order.ids to batch them in pool for update
            # 5. # update dateArchive on collective_offer
            with assert_num_queries(5):
                response = client.patch("/collective/offers-template/archive", json=data)

        # Then
        assert response.status_code == 204
        assert CollectiveOfferTemplate.query.get(offer1.id).isArchived
        assert CollectiveOfferTemplate.query.get(offer2.id).isArchived


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_when_archiving_all_existing_offers_template_when_cultural_partners_is_not_allowed_to(self, client):
        # Given
        offer1 = CollectiveOfferTemplateFactory()
        offer2 = CollectiveOfferTemplateFactory()
        venue = offer1.venue
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)

        # When
        client = client.with_session_auth("pro@example.com")
        data = {"ids": [offer1.id, offer2.id]}

        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
            return_value=False,
        ):
            response = client.patch("/collective/offers-template/archive", json=data)

        # Then
        assert response.status_code == 403
        assert response.json == {"Partner": ["User not in Adage can't edit the offer"]}
        assert offer1.isArchived is False
