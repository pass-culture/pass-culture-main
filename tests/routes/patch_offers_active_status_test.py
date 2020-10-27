from pcapi.models import OfferSQLEntity
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize
from pcapi.model_creators.generic_creators import (
    create_user,
    create_offerer,
    create_user_offerer,
    create_venue,
    API_URL,
)
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from tests.conftest import TestClient


class Returns204:
    def when_activating_existing_offers(self, app, db_session):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue, idx=1, is_active=False)
        offer2 = create_offer_with_thing_product(venue, idx=2, is_active=False)

        repository.save(offer1, offer2, user, user_offerer)

        json = {"ids": [humanize(offer1.id), humanize(offer2.id)], "isActive": True}

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch(f"{API_URL}/offers/active-status", json=json)
        )

        # Then
        assert response.status_code == 204
        assert response.json == None
        assert OfferSQLEntity.query.get(offer1.id).isActive == True
        assert OfferSQLEntity.query.get(offer2.id).isActive == True

    def when_deactivating_existing_offers(self, app, db_session):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue, idx=1, is_active=True)
        offer2 = create_offer_with_thing_product(venue, idx=2, is_active=True)

        repository.save(offer1, offer2, user, user_offerer)

        json = {"ids": [humanize(offer1.id), humanize(offer2.id)], "isActive": False}

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch(f"{API_URL}/offers/active-status", json=json)
        )

        # Then
        assert response.status_code == 204
        assert OfferSQLEntity.query.get(offer1.id).isActive == False
        assert OfferSQLEntity.query.get(offer2.id).isActive == False
