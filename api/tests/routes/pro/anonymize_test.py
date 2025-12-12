from unittest import mock

import pytest

import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.mark.features(WIP_PRO_AUTONOMOUS_ANONYMIZATION=True)
class Returns204Test:
    @mock.patch("pcapi.routes.pro.users.anonymize_pro_user", return_value=True)
    def test_anonymize_user_success(self, mock_anonymize_pro_user, client):
        user = users_factories.ProFactory()
        client = client.with_session_auth(email=user.email)

        response = client.post("/users/anonymize")

        assert response.status_code == 204
        mock_anonymize_pro_user.assert_called_once_with(user)


@pytest.mark.features(WIP_PRO_AUTONOMOUS_ANONYMIZATION=True)
class Returns400Test:
    @mock.patch("pcapi.routes.pro.users.anonymize_pro_user", return_value=False)
    def test_anonymize_user_not_anonymized(self, mock_anonymize_pro_user, client):
        user = users_factories.ProFactory()
        client = client.with_session_auth(email=user.email)

        response = client.post("/users/anonymize")

        assert response.status_code == 400
        assert response.json == {"global": ["Une erreur est survenue lors de l'anonymisation du compte"]}
        mock_anonymize_pro_user.assert_called_once_with(user)


@pytest.mark.features(WIP_PRO_AUTONOMOUS_ANONYMIZATION=False)
class Returns404Test:
    def test_feature_flag_disabled(self, client):
        user = users_factories.ProFactory()
        client = client.with_session_auth(email=user.email)

        response = client.post("/users/anonymize")

        assert response.status_code == 404
        assert response.json == {"global": "Cette fonctionnalité n'est pas disponible"}
