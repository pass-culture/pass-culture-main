from operator import itemgetter

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.utils.date import format_into_utc_date


pytestmark = pytest.mark.usefixtures("db_session")


class CollectiveOffersGetVenuesTest:
    num_queries = 1  # select api_key, offerer and provider
    num_queries += 1  # select venue, venue OA and address

    def test_list_venues(self, client):
        provider = providers_factories.ProviderFactory()
        venue1 = providers_factories.VenueProviderFactory(provider=provider).venue
        venue2 = providers_factories.VenueProviderFactory(provider=provider).venue
        offerers_factories.ApiKeyFactory(provider=provider)

        offerers_factories.VenueFactory()  # excluded from results

        with assert_num_queries(self.num_queries):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get("/v2/collective/venues")
            assert response.status_code == 200

        response_list = sorted(response.json, key=itemgetter("id"))
        assert response_list == [
            {
                "id": venue.id,
                "legalName": venue.name,
                "location": {
                    "address": venue.offererAddress.address.street,
                    "city": venue.offererAddress.address.city,
                    "postalCode": venue.offererAddress.address.postalCode,
                    "type": "physical" if not venue.isVirtual else "digital",
                },
                "siretComment": venue.comment,
                "createdDatetime": venue.dateCreated.isoformat(),
                "publicName": venue.publicName,
                "siret": venue.siret,
                "activityDomain": venue.venueTypeCode.name,
                "bookingUrl": None,
                "cancelUrl": None,
                "notificationUrl": None,
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

        with assert_num_queries(self.num_queries):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get("/v2/collective/venues")
            assert response.status_code == 200

        assert response.json == []

    def test_list_venues_anonymous_returns_401(self, client):
        offerers_factories.VenueFactory()

        with assert_num_queries(1):  # rollback
            response = client.get("/v2/collective/venues")
            assert response.status_code == 401


class GetOfferersVenuesTest:
    num_queries = 1  # select api_key, offerer and provider
    num_queries += 1  # select offerer, venue, venue OA and address
    num_queries += 1  # select provider
    num_queries += 1  # select venue_provider_external_urls

    def test_get_offerers_venues(self, client):
        provider = providers_factories.ProviderFactory()
        venue = providers_factories.VenueProviderFactory(provider=provider).venue
        offerers_factories.ApiKeyFactory(provider=provider)

        offerers_factories.VenueFactory()  # excluded from results

        with assert_num_queries(self.num_queries):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                "/public/offers/v1/offerer_venues"
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
                    "allowedOnAdage": offerer.allowedOnAdage,
                },
                "venues": [
                    {
                        "id": venue.id,
                        "legalName": venue.name,
                        "location": {
                            "address": venue.offererAddress.address.street,
                            "city": venue.offererAddress.address.city,
                            "postalCode": venue.offererAddress.address.postalCode,
                            "type": "physical" if not venue.isVirtual else "digital",
                        },
                        "siretComment": venue.comment,
                        "createdDatetime": format_into_utc_date(venue.dateCreated),
                        "publicName": venue.publicName,
                        "siret": venue.siret,
                        "bookingUrl": None,
                        "cancelUrl": None,
                        "notificationUrl": None,
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

        with assert_num_queries(self.num_queries):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                "/public/offers/v1/offerer_venues?siren=123456789"
            )
            assert response.status_code == 200

        assert len(response.json) == 1
        assert response.json[0]["offerer"]["siren"] == siren

        assert len(response.json[0]["venues"]) == 1
        assert response.json[0]["venues"][0]["id"] == venue.id

    def test_unauthenticated_client(self, client):
        with assert_num_queries(0):
            response = client.get("/public/offers/v1/offerer_venues?siren=123456789")
            assert response.status_code == 401
