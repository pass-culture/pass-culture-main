import pytest

from pcapi.utils.siren import SIRET_OR_RIDET_RE

from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


@pytest.mark.usefixtures("db_session")
class GetVenueTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/venues/{siret}"
    endpoint_method = "get"
    default_path_params = {"siret": 2}

    def test_should_raise_404_because_has_no_access_to_venue(self):
        plain_api_key, _ = self.setup_provider()
        venue = self.setup_venue()

        response = self.make_request(plain_api_key, path_params={"siret": venue.siret})

        assert response.status_code == 404
        assert response.json == {"global": "Venue cannot be found"}

    def test_should_raise_404_because_venue_provider_is_inactive(self):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()

        response = self.make_request(plain_api_key, path_params={"siret": venue_provider.venue.siret})

        assert response.status_code == 404
        assert response.json == {"global": "Venue cannot be found"}

    @pytest.mark.parametrize("invalid_siret", ["000000034000091", "0000000340000", "coucou"])
    def test_should_raise_400_because_siret_is_invalid(self, invalid_siret: str):
        plain_api_key, _ = self.setup_provider()

        response = self.make_request(plain_api_key, path_params={"siret": invalid_siret})

        assert response.status_code == 400
        assert response.json == {"siret": [f'string does not match regex "{SIRET_OR_RIDET_RE}"']}

    def test_should_return_venue(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        response = self.make_request(plain_api_key, path_params={"siret": venue_provider.venue.siret})

        assert response.status_code == 200
        assert response.json == {
            "accessibility": {
                "audioDisabilityCompliant": False,
                "mentalDisabilityCompliant": False,
                "motorDisabilityCompliant": False,
                "visualDisabilityCompliant": False,
            },
            "activityDomain": venue_provider.venue.venueTypeCode.name,
            "createdDatetime": f"{venue_provider.venue.dateCreated.isoformat()}Z",
            "id": venue_provider.venue.id,
            "legalName": venue_provider.venue.name,
            "location": {
                "address": venue_provider.venue.offererAddress.address.street,
                "city": venue_provider.venue.offererAddress.address.city,
                "postalCode": venue_provider.venue.offererAddress.address.postalCode,
                "type": "physical",
            },
            "publicName": venue_provider.venue.publicName,
            "siret": venue_provider.venue.siret,
            "siretComment": None,
            "bookingUrl": None,
            "cancelUrl": None,
            "notificationUrl": None,
        }
