from datetime import datetime

import pytest

from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.models import CollectiveOffer
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import assert_num_queries


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def when_archiving_existing_offers(self, client):
        # Given
        offer1 = CollectiveOfferFactory()
        venue = offer1.venue
        offer2 = CollectiveOfferFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)
        client = client.with_session_auth("pro@example.com")

        # When
        data = {"ids": [offer1.id, offer2.id]}

        # query += 1 authentication
        # query += 1 load current_user
        # query += 1 ensure there is no existing archived offer
        # query += 1 retrieve all collective_order.ids to batch them in pool for update
        # query += 1 update dateArchive on collective_offer
        with assert_num_queries(5):
            response = client.patch("/collective/offers/archive", json=data)

        # Then
        assert response.status_code == 204
        assert CollectiveOffer.query.get(offer1.id).isArchived
        assert CollectiveOffer.query.get(offer2.id).isArchived

    def when_archiving_existing_offers_from_other_offerer(self, client):
        # Given
        offer = CollectiveOfferFactory()
        venue = offer.venue
        offerer = venue.managingOfferer

        other_offer = CollectiveOfferFactory()
        other_venue = other_offer.venue
        other_offerer = other_venue.managingOfferer

        # Ensure that the offerer is different
        assert other_offerer.id != offerer.id

        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)
        client = client.with_session_auth("pro@example.com")

        # When
        data = {"ids": [offer.id, other_offer.id]}

        response = client.patch("/collective/offers/archive", json=data)

        # Then
        assert response.status_code == 204
        assert CollectiveOffer.query.get(offer.id).isArchived
        assert not CollectiveOffer.query.get(other_offer.id).isArchived


@pytest.mark.usefixtures("db_session")
class Returns422Test:
    def when_archiving_already_archived(self, client):
        # Given
        offer_already_archived = CollectiveOfferFactory(dateArchived=datetime.utcnow())
        venue = offer_already_archived.venue
        offer_not_archived = CollectiveOfferFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(user__email="pro@example.com", offerer=offerer)
        client = client.with_session_auth("pro@example.com")

        # When
        data = {"ids": [offer_already_archived.id, offer_not_archived.id]}

        response = client.patch("/collective/offers/archive", json=data)

        # Then
        assert response.status_code == 422
        assert response.json == {"global": ["One of the offer is already archived"]}

        assert CollectiveOffer.query.get(offer_already_archived.id).isArchived
        assert not CollectiveOffer.query.get(offer_not_archived.id).isArchived
