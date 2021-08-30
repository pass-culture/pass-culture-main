import pytest

import pcapi.core.offers.factories as offers_factories
from pcapi.models import UserOfferer

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class Returns202Test:
    def expect_user_offerer_attachment_to_be_validated(self, app):
        # Given
        user_offerer = offers_factories.UserOffererFactory(validationToken="TOKEN")

        # When
        response = TestClient(app.test_client()).get(
            "/validate/user-offerer/" + user_offerer.validationToken, headers={"origin": "http://localhost:3000"}
        )

        # Then
        assert response.status_code == 202
        assert response.data.decode("utf8") == "Validation du rattachement de la structure effectuée"

        user_offerer = UserOfferer.query.filter_by(id=user_offerer.id).first()

        assert user_offerer.isValidated


class Returns404Test:
    def test_user_offerer_attachment_not_to_be_validated_with_unknown_token(self, app):
        # When
        response = TestClient(app.test_client()).get("/validate/user-offerer/123")

        # Then
        assert response.status_code == 404
        assert (
            response.json["validation"][0]
            == "Aucun(e) objet ne correspond à ce code de validation ou l'objet est déjà validé"
        )
