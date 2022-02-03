import pytest

import pcapi.core.offers.factories as offers_factories
from pcapi.core.users import testing as sendinblue_testing
from pcapi.models.user_offerer import UserOfferer


pytestmark = pytest.mark.usefixtures("db_session")


class Returns202Test:
    def expect_user_offerer_attachment_to_be_validated(self, client):
        # Given
        user_offerer = offers_factories.UserOffererFactory(validationToken="TOKEN")

        # When
        response = client.get(f"/validate/user-offerer/{user_offerer.validationToken}")

        # Then
        assert response.status_code == 202
        assert response.data.decode("utf8") == "Validation du rattachement de la structure effectuée"

        user_offerer = UserOfferer.query.filter_by(id=user_offerer.id).first()

        assert user_offerer.isValidated

        assert len(sendinblue_testing.sendinblue_requests) == 1


class Returns404Test:
    def test_user_offerer_attachment_not_to_be_validated_with_unknown_token(self, client):
        # When
        response = client.get("/validate/user-offerer/123")

        # Then
        assert response.status_code == 404
        assert (
            response.json["validation"][0]
            == "Aucun(e) objet ne correspond à ce code de validation ou l'objet est déjà validé"
        )
