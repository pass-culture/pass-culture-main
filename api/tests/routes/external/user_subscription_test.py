from unittest.mock import patch

import freezegun
import pytest

from pcapi import settings
from pcapi.connectors.api_demarches_simplifiees import DMSGraphQLClient
from pcapi.connectors.api_demarches_simplifiees import GraphQLApplicationStates
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import factories as users_factories
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import ImportStatus

from tests.scripts.beneficiary.fixture import make_single_application


@pytest.mark.usefixtures("db_session")
class DmsWebhookApplicationTest:
    def test_dms_request_no_token(self, client):
        response = client.post("/webhooks/dms/application_status")
        assert response.status_code == 403

    def test_dms_request_no_params_with_token(self, client):
        response = client.post(f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}")

        assert response.status_code == 400

    @patch.object(DMSGraphQLClient, "execute_query")
    def test_dms_request(self, execute_query, client):
        execute_query.return_value = make_single_application(12, state="closed")
        form_data = {
            "procedure_id": "48860",
            "dossier_id": "6044787",
            "state": "en_construction",
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        response = client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 204
        assert execute_query.call_count == 1

    @patch.object(DMSGraphQLClient, "execute_query")
    @pytest.mark.parametrize(
        "dms_status,import_status",
        [
            (GraphQLApplicationStates.draft, ImportStatus.DRAFT),
            (GraphQLApplicationStates.on_going, ImportStatus.ONGOING),
            (GraphQLApplicationStates.refused, ImportStatus.REJECTED),
        ],
    )
    def test_dms_request_with_existing_user(self, execute_query, dms_status, import_status, client):
        user = users_factories.UserFactory(hasCompletedIdCheck=False)
        execute_query.return_value = make_single_application(12, state="closed", email=user.email)
        form_data = {
            "procedure_id": "48860",
            "dossier_id": "6044787",
            "state": dms_status.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        response = client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 204
        assert execute_query.call_count == 1

        beneficiary_import = BeneficiaryImport.query.one()
        assert beneficiary_import.source == BeneficiaryImportSources.demarches_simplifiees.value
        assert beneficiary_import.beneficiary == user
        assert len(beneficiary_import.statuses) == 1

        status = beneficiary_import.statuses[0]
        assert status.detail == "Webhook status update"
        assert status.status == import_status
        assert status.author == None

        assert user.hasCompletedIdCheck

    @freezegun.freeze_time("2021-10-30 09:00:00")
    @patch.object(DMSGraphQLClient, "execute_query")
    def test_dms_request_draft_application(self, execute_query, client):
        user = users_factories.UserFactory()
        execute_query.return_value = make_single_application(12, state="closed", email=user.email)

        form_data = {
            "procedure_id": "48860",
            "dossier_id": "6044787",
            "state": GraphQLApplicationStates.draft.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert len(user.subscriptionMessages) == 1
        assert user.subscriptionMessages[0].popOverIcon == subscription_models.PopOverIcon.FILE
        assert (
            user.subscriptionMessages[0].userMessage
            == "Nous avons bien reçu ton dossier le 30/10/2021. Rends toi sur la messagerie du site Démarches-Simplifiées pour être informé en temps réel."
        )

    @patch.object(DMSGraphQLClient, "execute_query")
    def test_dms_request_refused_application(self, execute_query, client):
        user = users_factories.UserFactory()
        execute_query.return_value = make_single_application(12, state="closed", email=user.email)

        form_data = {
            "procedure_id": "48860",
            "dossier_id": "6044787",
            "state": GraphQLApplicationStates.refused.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert len(user.subscriptionMessages) == 1
        assert user.subscriptionMessages[0].popOverIcon == subscription_models.PopOverIcon.ERROR
        assert (
            user.subscriptionMessages[0].userMessage
            == "Ton dossier déposé sur le site Démarches-Simplifiées a été rejeté. Tu n’es malheureusement pas éligible au pass culture."
        )

    @patch.object(DMSGraphQLClient, "execute_query")
    @patch.object(DMSGraphQLClient, "send_user_message")
    def test_dms_double_parsing_error(self, send_user_message, execute_query, client):
        form_data = {
            "procedure_id": "48860",
            "dossier_id": "6044787",
            "state": GraphQLApplicationStates.draft.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        execute_query.return_value = make_single_application(
            12, state="closed", email="toto@exemple.fr", postal_code="wrong_piece", id_piece_number="wrong_id_piece"
        )

        response = client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 204
        assert execute_query.call_count == 1
        assert send_user_message.call_count == 1
        assert (send_user_message.call_args[0][2]=="""Bonjour,
                                 
                                 Nous avons bien reçu ton dossier !
                                 Cependant, ton dossier ne peut pas être traiter pour la raison suivante :
                                 Un ou plusieurs champs ont été renseignés au mauvais format : 
                                 
                                 - le champ Code Postal
                                 - le champ Numéro de la pièce d’identité
                                 
                                 Pour que ton dossier soit traité, tu dois le modifier en faisant bien attention de remplir correctement toutes les informations (notamment ton code postal sous format 5 chiffres et le numéro de ta pièce d’identité sous format alphanumérique sans espace et sans caractères spéciaux).
                                 
                                 Pour avoir plus d’informations sur les étapes de ton inscription sur Démarches Simplifiées, je t’invite à consulter les articles suivants :
                                 
                                 Où puis-je trouver le numéro de ma pièce d'identité ? (https://aide.passculture.app/fr/articles/5100876-jeunes-ou-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-demarches-simplifiees)
                                 Comment bien renseigner mon adresse et mon code postal lors de l'inscription ? (https://aide.passculture.app/fr/articles/5508680-jeunes-ou-puis-je-trouver-le-numero-de-ma-piece-d-identite)
                                 
                                 
                                 Nous te souhaitons une belle journée.
                                 
                                 L’équipe pass Culture"""
                )


    @patch.object(DMSGraphQLClient, "execute_query")
    @patch.object(DMSGraphQLClient, "send_user_message")
    def test_dms_request_with_unexisting_user(self, send_user_message, execute_query, client):

        execute_query.return_value = make_single_application(
            12, state=GraphQLApplicationStates.draft.value, email="user@example.com"
        )
        form_data = {
            "procedure_id": "48860",
            "dossier_id": "6044787",
            "state": GraphQLApplicationStates.draft.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        response = client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 204
        assert execute_query.call_count == 1
        assert send_user_message.call_count == 1
        assert (
            send_user_message.call_args[0][2]
            == """Bonjour,
            
            Nous avons bien reçu ton dossier. Cependant, nous avons remarqué que tu n’es pas passé par l’application  avant de déposer le dossier ou que tu n’utilises pas la même adresse email sur le site Démarches Simplifiées.
            
            C’est pour cette raison que tu vas devoir poursuivre ton inscription en passant ton application.
            
            Pour cela, il faut :
            - Télécharger l’application sur ton smartphone
            - Entrer tes informations personnelles (nom, prénom, date de naissance, mail). Tu recevras alors un mail de confirmation (il peut se cacher dans tes spams, n’hésite pas à vérifier). 
            - Cliquer sur le lien de validation
            
            Une fois ton inscription faite, je t’invite à nous contacter pour que nous puissions t’indiquer les étapes à suivre.
            
            Nous te souhaitons une belle journée.
            
            L’équipe pass Culture"""
        )

    @patch.object(DMSGraphQLClient, "execute_query")
    @patch.object(DMSGraphQLClient, "send_user_message")
    def test_dms_id_piece_number_error(self, send_user_message, execute_query, client):
        user = users_factories.UserFactory()
        execute_query.return_value = make_single_application(
            12,
            state=GraphQLApplicationStates.draft.value,
            email=user.email,
            id_piece_number="wrong_value",
        )
        form_data = {
            "procedure_id": "48860",
            "dossier_id": "6044787",
            "state": GraphQLApplicationStates.draft.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        response = client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 204
        assert execute_query.call_count == 1
        assert send_user_message.call_count == 1
        assert (
            send_user_message.call_args[0][2]
            == """Bonjour, 
            
            Nous avons bien reçu ton dossier, mais le numéro de pièce d'identité sur le formulaire ne correspond pas à celui indiqué sur ta pièce d'identité.
            
            Cet article peut t’aider à le trouver sur ta pièce d'identité : https://aide.passculture.app/fr/articles/5508680-jeunes-ou-puis-je-trouver-le-numero-de-ma-piece-d-identite
            
            Peux-tu mettre à jour ton dossier sur le formulaire en ligne ?
            
            Pour t'aider à corriger ton dossier, merci de consulter cet article : https://aide.passculture.app/fr/articles/5100876-jeunes-ou-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-demarches-simplifiees
            
            Merci et à très vite,
            
            L'équipe du pass Culture"""
        )

    @patch.object(DMSGraphQLClient, "execute_query")
    @patch.object(DMSGraphQLClient, "send_user_message")
    def test_dms_postal_code_error(self, send_user_message, execute_query, client):
        user = users_factories.UserFactory()
        execute_query.return_value = make_single_application(
            12, state=GraphQLApplicationStates.draft.value, email=user.email, postal_code="6700000"
        )
        form_data = {
            "procedure_id": "48860",
            "dossier_id": "6044787",
            "state": GraphQLApplicationStates.draft.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        response = client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 204
        assert execute_query.call_count == 1
        assert send_user_message.call_count == 1
        assert (
            send_user_message.call_args[0][2]
            == """Bonjour,
            
            Le champ du code postal doit être rempli par 5 chiffres uniquement, sans lettres ni espace. Si tu as saisi ta ville dans le champ du code postal, merci de ne saisir que ces 5 chiffres.
            
            Pour corriger ton formulaire, cet article est là pour t'aider : https://aide.passculture.app/fr/articles/5100876-jeunes-ou-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-demarches-simplifiees]
            
            Très cordialement,
            
            L'équipe pass du Culture"""
        )