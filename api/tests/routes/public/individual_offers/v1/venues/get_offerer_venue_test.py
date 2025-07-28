import datetime

import pytest

from pcapi.core import testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import factories as providers_factories

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


@pytest.mark.usefixtures("db_session")
class GetOffererVenuesTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/public/offers/v1/offerer_venues"
    endpoint_method = "get"

    def create_multiple_venue_providers(self):
        plain_api_key, provider = self.setup_provider()
        offerer_with_two_venues = offerers_factories.OffererFactory(
            name="Offreur de fleurs", dateCreated=datetime.datetime(2022, 2, 22, 22, 22, 22), siren="123456789"
        )
        digital_venue = offerers_factories.VirtualVenueFactory(
            managingOfferer=offerer_with_two_venues,
            dateCreated=datetime.datetime(2023, 1, 16),
            name="Do you diji",
            publicName="Diji",
            venueTypeCode=offerers_models.VenueTypeCode.ARTISTIC_COURSE,
        )
        providers_factories.VenueProviderFactory(venue=digital_venue, provider=provider, venueIdAtOfferProvider="Test")
        physical_venue = offerers_factories.VenueFactory(
            managingOfferer=offerer_with_two_venues,
            dateCreated=datetime.datetime(2023, 1, 16, 1, 1, 1),
            name="Coiffeur Librairie",
            publicName="Tiff tuff",
            siret="12345678912345",
            venueTypeCode=offerers_models.VenueTypeCode.BOOKSTORE,
        )
        providers_factories.VenueProviderFactory(venue=physical_venue, provider=provider, venueIdAtOfferProvider="Test")

        offerer_with_one_venue = offerers_factories.OffererFactory(
            name="Offreur de prune", dateCreated=datetime.datetime(2022, 2, 22, 22, 22, 22), siren="123456781"
        )
        other_physical_venue = offerers_factories.VenueFactory(
            managingOfferer=offerer_with_one_venue,
            dateCreated=datetime.datetime(2023, 1, 16, 1, 1, 1),
            name="Toiletteur Librairie",
            publicName="wiff wuff",
            siret="12345678112345",
            venueTypeCode=offerers_models.VenueTypeCode.BOOKSTORE,
        )
        venue_provider = providers_factories.VenueProviderFactory(
            venue=other_physical_venue, provider=provider, venueIdAtOfferProvider="Test"
        )
        providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider,
            bookingExternalUrl="https://mysolution.com/booking",
            cancelExternalUrl="https://mysolution.com/cancel",
            notificationExternalUrl="https://mysolution.com/notif",
        )
        return (
            plain_api_key,
            offerer_with_two_venues,
            digital_venue,
            physical_venue,
            offerer_with_one_venue,
            other_physical_venue,
        )

    def test_get_offerer_venues(self):
        (
            plain_api_key,
            offerer_with_two_venues,
            digital_venue,
            physical_venue,
            offerer_with_one_venue,
            other_physical_venue,
        ) = self.create_multiple_venue_providers()

        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # select offerer, venue, venue oa and venue address
        num_queries += 1  # check provider exists
        num_queries += 1  # select venue_provider_external_urls
        num_queries += 1  # check provider exists
        num_queries += 1  # select venue_provider_external_urls
        num_queries += 1  # check provider exists
        num_queries += 1  # select venue_provider_external_urls

        with testing.assert_num_queries(num_queries):
            response = self.make_request(plain_api_key)
            assert response.status_code == 200

        assert len(response.json) == 2
        assert response.json[0] == {
            "offerer": {
                "createdDatetime": "2022-02-22T22:22:22Z",
                "id": offerer_with_two_venues.id,
                "name": "Offreur de fleurs",
                "siren": "123456789",
                "allowedOnAdage": offerer_with_two_venues.allowedOnAdage,
            },
            "venues": [
                {
                    "accessibility": {
                        "audioDisabilityCompliant": None,
                        "mentalDisabilityCompliant": None,
                        "motorDisabilityCompliant": None,
                        "visualDisabilityCompliant": None,
                    },
                    "activityDomain": "ARTISTIC_COURSE",
                    "createdDatetime": "2023-01-16T00:00:00Z",
                    "bookingUrl": None,
                    "cancelUrl": None,
                    "notificationUrl": None,
                    "id": digital_venue.id,
                    "legalName": "Do you diji",
                    "location": {"type": "digital"},
                    "publicName": "Diji",
                    "siret": None,
                    "siretComment": None,
                },
                {
                    "accessibility": {
                        "audioDisabilityCompliant": False,
                        "mentalDisabilityCompliant": False,
                        "motorDisabilityCompliant": False,
                        "visualDisabilityCompliant": False,
                    },
                    "activityDomain": "BOOKSTORE",
                    "createdDatetime": "2023-01-16T01:01:01Z",
                    "id": physical_venue.id,
                    "legalName": "Coiffeur Librairie",
                    "location": {
                        "address": physical_venue.offererAddress.address.street,
                        "city": physical_venue.offererAddress.address.city,
                        "postalCode": physical_venue.offererAddress.address.postalCode,
                        "type": "physical",
                    },
                    "publicName": "Tiff tuff",
                    "siret": "12345678912345",
                    "siretComment": None,
                    "bookingUrl": None,
                    "cancelUrl": None,
                    "notificationUrl": None,
                },
            ],
        }
        assert response.json[1] == {
            "offerer": {
                "createdDatetime": "2022-02-22T22:22:22Z",
                "id": offerer_with_one_venue.id,
                "name": "Offreur de prune",
                "siren": "123456781",
                "allowedOnAdage": offerer_with_one_venue.allowedOnAdage,
            },
            "venues": [
                {
                    "accessibility": {
                        "audioDisabilityCompliant": False,
                        "mentalDisabilityCompliant": False,
                        "motorDisabilityCompliant": False,
                        "visualDisabilityCompliant": False,
                    },
                    "activityDomain": "BOOKSTORE",
                    "createdDatetime": "2023-01-16T01:01:01Z",
                    "id": other_physical_venue.id,
                    "legalName": "Toiletteur Librairie",
                    "location": {
                        "address": other_physical_venue.offererAddress.address.street,
                        "city": other_physical_venue.offererAddress.address.city,
                        "postalCode": other_physical_venue.offererAddress.address.postalCode,
                        "type": "physical",
                    },
                    "publicName": "wiff wuff",
                    "siret": "12345678112345",
                    "siretComment": None,
                    "bookingUrl": "https://mysolution.com/booking",
                    "cancelUrl": "https://mysolution.com/cancel",
                    "notificationUrl": "https://mysolution.com/notif",
                }
            ],
        }

    def test_does_not_return_inactive_venue_providers(self):
        plain_api_key, provider = self.setup_provider()
        venue = self.setup_venue()
        providers_factories.VenueProviderFactory(venue=venue, provider=provider, isActive=False)

        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # select offerer
        with testing.assert_num_queries(num_queries):
            response = self.make_request(plain_api_key)
            assert response.status_code == 200

        assert response.json == []

    def test_get_filtered_offerer_venues(self, client):
        (
            plain_api_key,
            offerer_with_two_venues,
            _,
            _,
            _,
            _,
        ) = self.create_multiple_venue_providers()
        offerer_with_two_venues_siren = offerer_with_two_venues.siren

        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # select offerer, venue, venue OA and venue address
        num_queries += 1  # check provider exists
        num_queries += 1  # select venue_provider_external_urls
        num_queries += 1  # check provider exists
        num_queries += 1  # select venue_provider_external_urls

        with testing.assert_num_queries(num_queries):
            response = self.make_request(plain_api_key, query_params={"siren": offerer_with_two_venues_siren})
            assert response.status_code == 200

        json_dict = response.json
        assert len(json_dict) == 1
        assert json_dict[0]["offerer"]["siren"] == offerer_with_two_venues.siren
        assert len(json_dict[0]["venues"]) == 2

    @pytest.mark.parametrize("invalid_siren", ["1234567890", "1234890", "helloo"])
    def test_get_filtered_offerer_venues_with_siren_more_than_9_characters(self, invalid_siren):
        plain_api_key, _ = self.setup_provider()

        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # rollback atomic
        with testing.assert_num_queries(num_queries):
            response = self.make_request(plain_api_key, query_params={"siren": invalid_siren})
            assert response == 400

        assert response.json == {"siren": ['string does not match regex "^\\d{9}$"']}

    def test_when_no_venues(self):
        plain_api_key, _ = self.setup_provider()

        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # select offerer
        with testing.assert_num_queries(num_queries):
            response = self.make_request(plain_api_key)
            assert response.status_code == 200

        assert response.json == []
