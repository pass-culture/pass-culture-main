from operator import itemgetter

from flask import url_for
import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.utils.date import format_into_utc_date


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
            url_for("public_api.list_venues")
        )

        # Then
        assert response.status_code == 200

        response_list = sorted(response.json, key=itemgetter("id"))
        assert response_list == [
            {
                "id": venue.id,
                "legalName": venue.name,
                "location": {
                    "address": venue.street,
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
            url_for("public_api.list_venues")
        )

        # Then
        assert response.status_code == 200
        assert response.json == []

    def test_list_venues_anonymous_returns_401(self, client):
        # Given
        offerers_factories.VenueFactory()

        # When
        response = client.get(url_for("public_api.list_venues"))

        # Then
        assert response.status_code == 401


class GetOfferersVenuesTest:
    def test_get_offerers_venues(self, client):
        provider = providers_factories.ProviderFactory()
        venue = providers_factories.VenueProviderFactory(provider=provider).venue
        offerers_factories.ApiKeyFactory(provider=provider)

        offerers_factories.VenueFactory()  # excluded from results

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            url_for("public_api.get_offerer_venues")
        )

        assert response.status_code == 200

        offerer = venue.managingOfferer
        assert response.json == [
            {
                "offerer": {
                    "createdDatetime": format_into_utc_date(offerer.dateCreated),
                    "id": offerer.id,
                    "name": offerer.name,
                    "siren": offerer.siren,
                },
                "venues": [
                    {
                        "id": venue.id,
                        "legalName": venue.name,
                        "location": {
                            "address": venue.street,
                            "city": venue.city,
                            "postalCode": venue.postalCode,
                            "type": "physical" if not venue.isVirtual else "digital",
                        },
                        "siretComment": venue.comment,
                        "createdDatetime": format_into_utc_date(venue.dateCreated),
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
                ],
            }
        ]

    def test_filter_offerers_venues_by_siren(self, client):
        siren = "123456789"

        provider = providers_factories.ProviderFactory()
        venue = providers_factories.VenueProviderFactory(venue__managingOfferer__siren=siren, provider=provider).venue
        offerers_factories.ApiKeyFactory(provider=provider)

        providers_factories.VenueProviderFactory(provider=provider)  # excluded

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            url_for("public_api.get_offerer_venues", siren=siren)
        )

        assert response.status_code == 200

        assert len(response.json) == 1
        assert response.json[0]["offerer"]["siren"] == siren

        assert len(response.json[0]["venues"]) == 1
        assert response.json[0]["venues"][0]["id"] == venue.id

    def test_filter_offerers_venues_by_siren_error(self, client):
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            url_for("public_api.get_offerer_venues", siren="not a siren")
        )
        assert response.status_code == 400

    def test_unauthenticated_client(self, client):
        response = client.get(url_for("public_api.get_offerer_venues", siren="123456789"))
        assert response.status_code == 401
