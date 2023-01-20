from operator import itemgetter

from flask import url_for
import pytest

import pcapi.core.offerers.factories as offerers_factories


@pytest.mark.usefixtures("db_session")
class CollectiveOffersGetVenuesTest:
    def test_list_venues(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        venue1 = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue2 = offerers_factories.VenueFactory(managingOfferer=offerer)
        offerers_factories.ApiKeyFactory(offerer=offerer)

        offerers_factories.VenueFactory()  # excluded from results

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            url_for("pro_public_api_v2.list_venues")
        )

        # Then
        assert response.status_code == 200

        response_list = sorted(response.json, key=itemgetter("id"))
        assert response_list == [
            {
                "id": venue.id,
                "name": venue.name,
                "address": venue.address,
                "postalCode": venue.postalCode,
                "city": venue.city,
            }
            for venue in [venue1, venue2]
        ]

    def test_list_venues_empty(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)

        offerers_factories.VenueFactory()  # excluded from results

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            url_for("pro_public_api_v2.list_venues")
        )

        # Then
        assert response.status_code == 200
        assert response.json == []

    def test_list_venues_user_auth_returns_401(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offerers_factories.ApiKeyFactory(offerer=user_offerer.offerer)

        # When
        response = client.with_session_auth(user_offerer.user.email).get(url_for("pro_public_api_v2.list_venues"))

        # Then
        assert response.status_code == 401

    def test_list_venues_anonymous_returns_401(self, client):
        # Given
        offerers_factories.VenueFactory()

        # When
        response = client.get(url_for("pro_public_api_v2.list_venues"))

        # Then
        assert response.status_code == 401
