from typing import ByteString

import pytest

import pcapi.core.offerers.factories as offerers_factories

from tests.conftest import TestClient
from tests.routes.adage_iframe.utils_create_test_token import create_adage_jwt_fake_valid_token


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    def _create_adage_valid_token(self) -> ByteString:
        return create_adage_jwt_fake_valid_token(
            civility="Mme.",
            lastname="GRIS",
            firstname="Laurence",
            email="laurence.gris@example.com",
            uai=None,
        )

    def test_return_venue_with_publicName_of_given_siret(self, app):
        # Given
        requested_venue = offerers_factories.VenueFactory(publicName="Un petit surnom")
        offerers_factories.VenueFactory()
        valid_encoded_token = self._create_adage_valid_token()

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {valid_encoded_token}"}

        # When
        response = test_client.get(f"/adage-iframe/venues/{requested_venue.siret}")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "id": requested_venue.id,
            "name": requested_venue.name,
            "publicName": requested_venue.publicName,
        }

    def test_return_venue_without_publicName_of_given_siret(self, app):
        # Given
        requested_venue = offerers_factories.VenueFactory(publicName=None)
        offerers_factories.VenueFactory()
        valid_encoded_token = self._create_adage_valid_token()

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {valid_encoded_token}"}

        # When
        response = test_client.get(f"/adage-iframe/venues/{requested_venue.siret}")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "id": requested_venue.id,
            "name": requested_venue.name,
            "publicName": None,
        }


class ReturnsErrorTest:
    def _create_adage_valid_token(self) -> ByteString:
        return create_adage_jwt_fake_valid_token(
            civility="M.",
            lastname="POINTÉ",
            firstname="Vincent",
            email="vincent.pointé@example.com",
            uai=None,
        )

    def test_return_error_if_venue_does_not_exist(self, app):
        # Given
        offerers_factories.VenueFactory()
        valid_encoded_token = self._create_adage_valid_token()

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {valid_encoded_token}"}

        # When
        response = test_client.get("/adage-iframe/venues/123456789")

        # Then
        assert response.status_code == 404
        assert response.json == {"siret": "Aucun lieu n'existe pour ce siret"}
