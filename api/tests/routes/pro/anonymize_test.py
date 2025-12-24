import logging
from unittest import mock

import pytest

import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")

logger = logging.getLogger(__name__)


@pytest.mark.features(WIP_PRO_AUTONOMOUS_ANONYMIZATION=True)
class Returns204Test:
    @mock.patch("pcapi.routes.pro.users.transactional_mails.send_anonymization_confirmation_email_to_pro")
    @mock.patch("pcapi.routes.pro.users.anonymize_pro_user", return_value=True)
    @mock.patch("pcapi.routes.pro.users.gdpr_api.can_anonymise_pro_user", return_value=True)
    def test_anonymize_user_success(self, mock_can_anonymise, mock_anonymize_pro_user, mock_send_mail, client, caplog):
        user = users_factories.ProFactory()
        client = client.with_session_auth(email=user.email)

        with caplog.at_level(logging.INFO):
            response = client.post("/users/anonymize")

        assert response.status_code == 204
        assert next(rec for rec in caplog.records if rec.msg == "User has been anonymized")
        mock_can_anonymise.assert_called_once_with(user)
        mock_anonymize_pro_user.assert_called_once_with(
            user=user, author=user, action_history_comment="Demande d’anonymisation depuis l’espace partenaire"
        )
        mock_send_mail.assert_called_once_with(user.email)


@pytest.mark.features(WIP_PRO_AUTONOMOUS_ANONYMIZATION=True)
class Returns400Test:
    @mock.patch("pcapi.routes.pro.users.transactional_mails.send_anonymization_confirmation_email_to_pro")
    @mock.patch("pcapi.routes.pro.users.anonymize_pro_user", return_value=False)
    @mock.patch("pcapi.routes.pro.users.gdpr_api.can_anonymise_pro_user", return_value=True)
    def test_anonymize_user_not_anonymized(self, mock_can_anonymise, mock_anonymize_pro_user, mock_send_mail, client):
        user = users_factories.ProFactory()
        client = client.with_session_auth(email=user.email)

        response = client.post("/users/anonymize")

        assert response.status_code == 400
        assert response.json == {"global": ["Une erreur est survenue lors de l'anonymisation du compte"]}
        mock_can_anonymise.assert_called_once_with(user)
        mock_anonymize_pro_user.assert_called_once_with(
            user=user, author=user, action_history_comment="Demande d’anonymisation depuis l’espace partenaire"
        )
        mock_send_mail.assert_not_called()


@pytest.mark.features(WIP_PRO_AUTONOMOUS_ANONYMIZATION=True)
class Returns403Test:
    @mock.patch("pcapi.routes.pro.users.transactional_mails.send_anonymization_confirmation_email_to_pro")
    @mock.patch("pcapi.routes.pro.users.anonymize_pro_user")
    @mock.patch("pcapi.routes.pro.users.gdpr_api.can_anonymise_pro_user", return_value=False)
    def test_anonymize_user_not_eligible(self, mock_can_anonymise, mock_anonymize_pro_user, mock_send_mail, client):
        user = users_factories.ProFactory()
        client = client.with_session_auth(email=user.email)

        response = client.post("/users/anonymize")

        assert response.status_code == 403
        assert response.json == {"global": ["Le compte ne peut pas être anonymisé de manière autonome"]}
        mock_can_anonymise.assert_called_once_with(user)
        mock_anonymize_pro_user.assert_not_called()
        mock_send_mail.assert_not_called()


@pytest.mark.features(WIP_PRO_AUTONOMOUS_ANONYMIZATION=False)
class Returns404Test:
    def test_feature_flag_disabled(self, client):
        user = users_factories.ProFactory()
        client = client.with_session_auth(email=user.email)

        response = client.post("/users/anonymize")

        assert response.status_code == 404
        assert response.json == {"global": "Cette fonctionnalité n'est pas disponible"}
