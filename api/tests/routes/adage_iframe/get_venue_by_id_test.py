from typing import ByteString

import pytest

import pcapi.core.offerers.factories as offerers_factories

from tests.routes.adage_iframe.utils_create_test_token import create_adage_jwt_default_fake_valid_token


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    def _create_adage_valid_token(self) -> ByteString:
        return create_adage_jwt_default_fake_valid_token(
            civility="Mme.",
            lastname="GRIS",
            firstname="Laurence",
            email="laurence.gris@example.com",
            uai=None,
        )

    def test_return_venue_with_publicName_of_given_id(self, client):
        # Given
        requested_venue = offerers_factories.VenueFactory(publicName="Un petit surnom", isPermanent=True)
        offerers_factories.VenueFactory(managingOfferer=requested_venue.managingOfferer, isPermanent=True)
        offerers_factories.VenueFactory(isPermanent=True)
        valid_encoded_token = self._create_adage_valid_token()

        client.auth_header = {"Authorization": f"Bearer {valid_encoded_token}"}

        # When
        response = client.get(f"/adage-iframe/venues/{requested_venue.id}")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "id": requested_venue.id,
            "name": requested_venue.name,
            "publicName": requested_venue.publicName,
            "relative": [],
        }

    def test_return_venue_without_publicName_of_given_id(self, client):
        # Given
        requested_venue = offerers_factories.VenueFactory(publicName=None, isPermanent=True)
        offerers_factories.VenueFactory(managingOfferer=requested_venue.managingOfferer, isPermanent=True)
        offerers_factories.VenueFactory(isPermanent=True)
        valid_encoded_token = self._create_adage_valid_token()

        client.auth_header = {"Authorization": f"Bearer {valid_encoded_token}"}

        # When
        response = client.get(f"/adage-iframe/venues/{requested_venue.id}")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "id": requested_venue.id,
            "name": requested_venue.name,
            "publicName": None,
            "relative": [],
        }

    def test_relative_venue(self, client):
        # Given
        requested_venue = offerers_factories.VenueFactory(publicName=None, isPermanent=True)
        venue2 = offerers_factories.VenueFactory(managingOfferer=requested_venue.managingOfferer, isPermanent=True)
        venue3 = offerers_factories.VenueFactory(managingOfferer=requested_venue.managingOfferer, isPermanent=False)
        offerers_factories.VenueFactory(isPermanent=True)
        valid_encoded_token = self._create_adage_valid_token()

        client.auth_header = {"Authorization": f"Bearer {valid_encoded_token}"}

        # When
        response = client.get(f"/adage-iframe/venues/{requested_venue.id}?getRelative=true")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "id": requested_venue.id,
            "name": requested_venue.name,
            "publicName": None,
            "relative": [venue2.id, venue3.id],
        }


class ReturnsErrorTest:
    def _create_adage_valid_token(self) -> ByteString:
        return create_adage_jwt_default_fake_valid_token(
            civility="M.",
            lastname="POINTÉ",
            firstname="Vincent",
            email="vincent.pointé@example.com",
            uai=None,
        )

    def test_return_error_if_venue_does_not_exist(self, client):
        # Given
        offerers_factories.VenueFactory(isPermanent=True)
        valid_encoded_token = self._create_adage_valid_token()

        client.auth_header = {"Authorization": f"Bearer {valid_encoded_token}"}

        # When
        response = client.get("/adage-iframe/venues/123456789")

        # Then
        assert response.status_code == 404
        assert response.json == {"venue_id": "Aucun lieu n'existe pour ce venue_id"}
