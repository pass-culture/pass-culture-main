from operator import itemgetter

from flask import url_for
import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories


pytestmark = pytest.mark.usefixtures("db_session")


class CollectiveOffersGetVenuesTest:
    def test_list_venues(self, client):
        # Given
        provider = providers_factories.ProviderFactory()
        venue1 = providers_factories.VenueProviderFactory(provider=provider).venue
        venue2 = providers_factories.VenueProviderFactory(provider=provider).venue
        offerers_factories.ApiKeyFactory(provider=provider)

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
                "legalName": venue.name,
                "location": {
                    "address": venue.address,
                    "city": venue.city,
                    "postalCode": venue.postalCode,
                    "type": "physical" if not venue.isVirtual else "digital",
                },
                "siretComment": venue.comment,
                "createdDatetime": venue.dateCreated.isoformat(),
                "publicName": venue.publicName,
                "siret": venue.siret,
                "activityDomain": venue.venueTypeCode.name,
                "accessibility": {
                    "audioDisabilityCompliant": venue.audioDisabilityCompliant,
                    "mentalDisabilityCompliant": venue.mentalDisabilityCompliant,
                    "motorDisabilityCompliant": venue.motorDisabilityCompliant,
                    "visualDisabilityCompliant": venue.visualDisabilityCompliant,
                },
            }
            for venue in [venue1, venue2]
        ]

    def test_list_venues_empty(self, client):
        provider = providers_factories.ProviderFactory()
        offerers_factories.ApiKeyFactory(provider=provider)

        offerers_factories.VenueFactory()  # excluded from results

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            url_for("pro_public_api_v2.list_venues")
        )

        # Then
        assert response.status_code == 200
        assert response.json == []

    def test_list_venues_anonymous_returns_401(self, client):
        # Given
        offerers_factories.VenueFactory()

        # When
        response = client.get(url_for("pro_public_api_v2.list_venues"))

        # Then
        assert response.status_code == 401
