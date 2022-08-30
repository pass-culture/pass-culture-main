import datetime
import json
import logging
import time
import typing
from unittest import mock
from unittest.mock import patch
import uuid

from dateutil import relativedelta
import freezegun
import pytest

from pcapi import settings
from pcapi.connectors.dms import api as api_dms
from pcapi.connectors.dms import models as dms_models
from pcapi.core import testing
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.ubble import api as ubble_fraud_api
from pcapi.core.fraud.ubble import models as ubble_fraud_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users.api import get_domains_credit
from pcapi.models import db
from pcapi.repository import repository
from pcapi.validation.routes import ubble as ubble_routes

from tests.core.subscription import test_factories
from tests.scripts.beneficiary.fixture import make_single_application
from tests.test_utils import json_default


@pytest.mark.usefixtures("db_session")
class DmsWebhookApplicationTest:
    def test_dms_request_no_token(self, client):
        response = client.post("/webhooks/dms/application_status")
        assert response.status_code == 403

    def test_dms_request_no_params_with_token(self, client):
        response = client.post(f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}")

        assert response.status_code == 400

    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_dms_request(self, execute_query, client):
        user = users_factories.UserFactory()
        execute_query.return_value = make_single_application(
            12, state=dms_models.GraphQLApplicationStates.accepted, email=user.email
        )
        form_data = {
            "procedure_id": 48860,
            "dossier_id": 6044787,
            "state": "accepte",
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        response = client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 204
        assert execute_query.call_count == 1

    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    @pytest.mark.parametrize(
        "dms_status,fraud_check_status",
        [
            (dms_models.GraphQLApplicationStates.draft, fraud_models.FraudCheckStatus.STARTED),
            (dms_models.GraphQLApplicationStates.on_going, fraud_models.FraudCheckStatus.PENDING),
            (dms_models.GraphQLApplicationStates.refused, fraud_models.FraudCheckStatus.KO),
        ],
    )
    def test_dms_request_with_existing_user(self, execute_query, dms_status, fraud_check_status, client):
        user = users_factories.UserFactory()
        execute_query.return_value = make_single_application(6044787, state=dms_status.value, email=user.email)
        form_data = {
            "procedure_id": 48860,
            "dossier_id": 6044787,
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

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.first()
        assert fraud_check.type == fraud_models.FraudCheckType.DMS
        assert fraud_check.userId == user.id
        assert fraud_check.status == fraud_check_status

        assert fraud_api.has_user_performed_identity_check(user)

    @freezegun.freeze_time("2022-03-17 09:00:00")
    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_dms_pc_14151(self, execute_query, client):
        """
        Scenario from reported bug PC-14151.
        Eligible young user did not become beneficiary after DMS application approved.
        Unit tests uses RAW data retrieved from DMS, then anonymized
        """
        user = users_factories.UserFactory(
            email="young@example.com",
            dateOfBirth=datetime.datetime.combine(datetime.date(2003, 5, 5), datetime.time(0, 0)),
            firstName="Young",
            lastName="Beneficiary",
            publicName="Young Beneficiary",
            phoneNumber="+33746050403",
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )

        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=None,
        )

        execute_query.return_value = {
            "dossier": {
                "id": "RG9zc2llci03MDA2NzYz",
                "number": 7654321,
                "archived": False,
                "state": "accepte",
                "dateDepot": "2022-03-17T12:19:37+01:00",
                "dateDerniereModification": "2022-03-23T10:22:01+01:00",
                "datePassageEnConstruction": "2022-03-17T12:19:37+01:00",
                "datePassageEnInstruction": "2022-03-22T16:58:25+01:00",
                "dateTraitement": "2022-03-22T16:58:28+01:00",
                "demarche": {
                    "id": "RG9zc2llci03MDA2NzYa",
                    "number": 45678,
                },
                "instructeurs": [{"id": "SW5zdHJ1Y3RldXItNDk5Nzg=", "email": "admin@example.com"}],
                "groupeInstructeur": {"id": "R3JvdXBlSW5zdHJ1Y3RldXItNjEyNzE=", "number": 12345, "label": "défaut"},
                "champs": [
                    {
                        "id": "Q2hhbXAtNjA5NDQ3",
                        "label": "Comment remplir ce formulaire de pré-inscription au pass Culture ?",
                        "stringValue": "",
                    },
                    {
                        "id": "Q2hhbXAtNTgyMjIw",
                        "label": "Quelle est ta date de naissance ?",
                        "stringValue": "05 mai 2003",
                    },
                    {
                        "id": "Q2hhbXAtNTgyMjE5",
                        "label": "Quel est ton numéro de téléphone ?",
                        "stringValue": "07 06 05 04 03",
                    },
                    {"id": "Q2hhbXAtNzE4MDk0", "label": "Merci d' indiquer ton statut", "stringValue": "Étudiant"},
                    {"id": "Q2hhbXAtMjI3MTA3MQ==", "label": "Document d'identité", "stringValue": ""},
                    {"id": "Q2hhbXAtNzE4MjIy", "label": "Pièces justificatives acceptées", "stringValue": ""},
                    {"id": "Q2hhbXAtNDU5ODE5", "label": "Pièce d'identité (page avec votre photo)", "stringValue": ""},
                    {"id": "Q2hhbXAtMjAyMTk4MQ==", "label": "Ton selfie avec ta pièce d'identité  ", "stringValue": ""},
                    {
                        "id": "Q2hhbXAtMjAyMTk4Mw==",
                        "label": "Quel est le numéro de la pièce que tu viens de saisir ?",
                        "stringValue": "9X8Y7654Z",
                    },
                    {"id": "Q2hhbXAtNDUxMjg0", "label": "Déclaration de résidence", "stringValue": ""},
                    {
                        "id": "Q2hhbXAtMjAxMTQxNQ==",
                        "label": "Justificatif de domicile - Documents",
                        "stringValue": "",
                        "champs": [
                            {"id": "Q2hhbXAtMjI3MzY2Mw==", "label": "Justificatif de domicile ", "stringValue": ""},
                            {"id": "Q2hhbXAtMjI3MzY2MQ==", "label": "Attestation d'hébergement ", "stringValue": ""},
                            {
                                "id": "Q2hhbXAtMjI3MzY2Mg==",
                                "label": "Document d'identité du responsable légal",
                                "stringValue": "",
                            },
                        ],
                    },
                    {
                        "id": "Q2hhbXAtNTgyMjIx",
                        "label": "Quel est le code postal de ta commune de résidence ?",
                        "stringValue": "06000",
                    },
                    {
                        "id": "Q2hhbXAtNTgyMjIz",
                        "label": "Quelle est ton adresse de résidence ?",
                        "stringValue": "1 Promenade des Anglais 06000 Nice",
                    },
                    {
                        "id": "Q2hhbXAtNzE4MjU0",
                        "label": "Je certifie sur l’honneur résider légalement et habituellement sur le territoire français depuis plus de un an.",
                        "stringValue": "true",
                    },
                    {
                        "id": "Q2hhbXAtNDY2Njk1",
                        "label": "Consentement à l'utilisation de mes données",
                        "stringValue": "",
                    },
                    {
                        "id": "Q2hhbXAtNDY2Njk0",
                        "label": "J'accepte les conditions générales d'utilisation du pass Culture",
                        "stringValue": "true",
                    },
                    {
                        "id": "Q2hhbXAtNDU3MzAz",
                        "label": "Je donne mon accord au traitement de mes données à caractère personnel. *",
                        "stringValue": "true",
                    },
                    {
                        "id": "Q2hhbXAtMTE0NTg4Mg==",
                        "label": "Je déclare sur l’honneur que l'ensemble des réponses et documents fournis sont corrects et authentiques.",
                        "stringValue": "true",
                    },
                    {
                        "id": "Q2hhbXAtNDU0Nzc1",
                        "label": "Un grand merci et à très vite sur le pass Culture !",
                        "stringValue": "",
                    },
                ],
                "messages": [],
                "annotations": [],
                "usager": {"id": "VXNlci0yMzA4Mjg0", "email": "young@example.com"},
                "demandeur": {
                    "id": "SW5kaXZpZHVhbC01MDYxNjMw",
                    "civilite": "Mme",
                    "nom": "Beneficiary",
                    "prenom": "Young",
                    "dateDeNaissance": None,
                },
            }
        }
        form_data = {
            "procedure_id": 45678,
            "dossier_id": 7654321,
            "state": dms_models.GraphQLApplicationStates.accepted.value,
            "updated_at": "2022-03-17 08:00:00 +0100",
        }
        response = client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 204
        assert execute_query.call_count == 1

        fraud_check = (
            fraud_models.BeneficiaryFraudCheck.query.filter(
                fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS
            )
            .order_by(fraud_models.BeneficiaryFraudCheck.id.desc())
            .first()
        )

        assert fraud_check.userId == user.id
        assert fraud_check.status == fraud_models.FraudCheckStatus.OK
        assert fraud_check.eligibilityType == users_models.EligibilityType.AGE18

        content = fraud_check.source_data()
        assert content.activity == "Étudiant"
        assert content.address == "1 Promenade des Anglais 06000 Nice"
        assert content.application_number == 7654321
        assert content.birth_date == datetime.date(2003, 5, 5)
        assert content.city == None
        assert content.civility == users_models.GenderEnum.F
        assert content.department == None
        assert content.email == "young@example.com"
        assert content.first_name == "Young"
        assert content.id_piece_number == "9X8Y7654Z"
        assert content.last_name == "Beneficiary"
        assert content.phone == "0706050403"
        assert content.postal_code == "06000"
        assert content.procedure_number == 45678
        assert content.state == "accepte"
        assert content.registration_datetime == datetime.datetime(
            2022, 3, 17, 12, 19, 37, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))
        )

        db.session.refresh(user)

        assert fraud_api.has_user_performed_identity_check(user)
        assert user.has_beneficiary_role

        domains_credit = get_domains_credit(user)
        assert domains_credit.all.initial == 300
        assert domains_credit.all.remaining == 300

    @freezegun.freeze_time("2021-10-30 09:00:00")
    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_dms_request_draft_application(self, execute_query, client):
        user = users_factories.UserFactory()
        execute_query.return_value = make_single_application(
            12, state=dms_models.GraphQLApplicationStates.draft, email=user.email
        )

        form_data = {
            "procedure_id": 48860,
            "dossier_id": 6044787,
            "state": dms_models.GraphQLApplicationStates.draft.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert len(user.beneficiaryFraudChecks) == 1
        fraud_check = user.beneficiaryFraudChecks[0]
        assert fraud_check.type == fraud_models.FraudCheckType.DMS
        assert fraud_check.status == fraud_models.FraudCheckStatus.STARTED
        assert fraud_check.source_data().state == "en_construction"
        assert len(user.subscriptionMessages) == 1
        assert user.subscriptionMessages[0].popOverIcon == subscription_models.PopOverIcon.FILE
        assert (
            user.subscriptionMessages[0].userMessage
            == "Nous avons bien reçu ton dossier le 30/10/2021. Rends-toi sur la messagerie du site Démarches-Simplifiées pour être informé en temps réel."
        )

    @freezegun.freeze_time("2021-10-30 09:00:00")
    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_dms_request_on_going_application(self, execute_query, client):
        user = users_factories.UserFactory()
        execute_query.return_value = make_single_application(
            12, state=dms_models.GraphQLApplicationStates.on_going, email=user.email
        )

        form_data = {
            "procedure_id": 48860,
            "dossier_id": 6044787,
            "state": dms_models.GraphQLApplicationStates.on_going.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert len(user.subscriptionMessages) == 1
        assert len(user.beneficiaryFraudChecks) == 1
        fraud_check = user.beneficiaryFraudChecks[0]
        assert fraud_check.type == fraud_models.FraudCheckType.DMS
        assert fraud_check.status == fraud_models.FraudCheckStatus.PENDING
        assert fraud_check.source_data().state == "en_instruction"
        assert user.subscriptionMessages[0].popOverIcon == subscription_models.PopOverIcon.FILE
        assert (
            user.subscriptionMessages[0].userMessage
            == "Nous avons bien reçu ton dossier le 30/10/2021. Rends-toi sur la messagerie du site Démarches-Simplifiées pour être informé en temps réel."
        )

    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_dms_request_refused_application(self, execute_query, client):
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.DMS, thirdPartyId="12")
        execute_query.return_value = make_single_application(
            12, state=dms_models.GraphQLApplicationStates.refused, email=user.email
        )

        form_data = {
            "procedure_id": 48860,
            "dossier_id": 12,
            "state": dms_models.GraphQLApplicationStates.refused.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert len(user.subscriptionMessages) == 1
        assert len(user.beneficiaryFraudChecks) == 1
        fraud_check = user.beneficiaryFraudChecks[0]
        assert fraud_check.type == fraud_models.FraudCheckType.DMS
        assert fraud_check.status == fraud_models.FraudCheckStatus.KO
        assert fraud_check.source_data().state == "refuse"
        assert user.subscriptionMessages[0].popOverIcon == subscription_models.PopOverIcon.ERROR
        assert (
            user.subscriptionMessages[0].userMessage
            == "Ton dossier déposé sur le site Démarches-Simplifiées a été refusé : tu n’es malheureusement pas éligible au pass Culture."
        )
        assert fraud_check.reasonCodes == [fraud_models.FraudReasonCode.REFUSED_BY_OPERATOR]

    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    @patch.object(api_dms.DMSGraphQLClient, "send_user_message")
    def test_dms_double_field_error(self, send_user_message, execute_query, client):
        user = users_factories.UserFactory()
        form_data = {
            "procedure_id": 48860,
            "dossier_id": 6044787,
            "state": dms_models.GraphQLApplicationStates.draft.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        execute_query.return_value = make_single_application(
            12,
            state=dms_models.GraphQLApplicationStates.draft.value,
            email=user.email,
            postal_code="error_postal_code",
            id_piece_number="error_identity_piece_number",
        )
        response = client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 204
        assert execute_query.call_count == 1
        assert send_user_message.call_count == 1
        assert send_user_message.call_args[0][2] == (
            "Bonjour,\n"
            "\n"
            "Nous avons bien reçu ton dossier, mais il y a une erreur dans les champs suivants, inscrits sur le formulaire en ligne:\n"
            " - ta pièce d'identité\n"
            " - ton code postal\n"
            "\n"
            "Pour que ton dossier soit traité, tu dois le modifier en faisant bien attention à remplir correctement toutes les informations.\n"
            "Pour avoir plus d’informations sur les étapes de ton inscription sur Démarches Simplifiées, nous t’invitons à consulter les articles suivants :\n"
            'Jeune de 18 ans : <a href="https://aide.passculture.app/hc/fr/articles/4411991957521--Jeunes-Comment-remplir-le-formulaire-sur-D%C3%A9marches-Simplifi%C3%A9es-">[Jeunes] Comment remplir le formulaire sur Démarches Simplifiées?</a>\n'
            'Jeune de 15 à 17 ans : <a href="https://aide.passculture.app/hc/fr/articles/4404373671324--Jeunes-15-17-ans-Comment-remplir-le-formulaire-sur-D%C3%A9marches-Simplifi%C3%A9es-">[Jeunes 15-17 ans] Comment remplir le formulaire sur Démarches Simplifiées?</a>\n'
            "\n"
            "Ton code postal doit être renseigné sous format 5 chiffres uniquement, sans lettre ni espace\n"
            '<a href="https://aide.passculture.app/hc/fr/articles/4411998995985--Jeunes-Comment-bien-renseigner-mon-adresse-et-mon-code-postal-lors-de-l-inscription-">Comment bien renseigner mon adresse et mon code postal lors de l’inscription ? </a>\n'
            "\n"
            "Ton numéro de pièce d’identité doit être renseigné sous format alphanumérique sans espace et sans caractères spéciaux\n"
            '<a href="https://aide.passculture.app/hc/fr/articles/4411999008657--Jeunes-Où-puis-je-trouver-le-numéro-de-ma-pièce-d-identité">Où puis-je trouver le numéro de ma pièce d’identité ?</a>\n'
            "\n"
            "Merci de corriger ton dossier.\n"
            "\n"
            'Tu trouveras de l’aide dans cet article : <a href="https://aide.passculture.app/hc/fr/articles/4411999116433--Jeunes-Où-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-Démarches-Simplifiées-">Où puis-je trouver de l’aide concernant mon dossier d’inscription sur Démarches Simplifiées ?</a>\n'
            "\n"
            "Nous te souhaitons une belle journée.\n"
            "\n"
            "L’équipe du pass Culture"
        )
        assert len(user.subscriptionMessages) == 1
        assert user.subscriptionMessages[0].popOverIcon == subscription_models.PopOverIcon.WARNING
        assert (
            user.subscriptionMessages[0].userMessage
            == "Il semblerait que les champs ‘ta pièce d'identité, ton code postal’ soient erronés. Tu peux te rendre sur le site Démarches-simplifiées pour les rectifier."
        )

        fraud_check = user.beneficiaryFraudChecks[0]
        assert fraud_check.type == fraud_models.FraudCheckType.DMS
        assert fraud_check.status == fraud_models.FraudCheckStatus.STARTED
        assert (
            fraud_check.reason
            == "Erreur dans les données soumises dans le dossier DMS : 'id_piece_number' (error_identity_piece_number),'postal_code' (error_postal_code)"
        )

    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    @patch.object(api_dms.DMSGraphQLClient, "send_user_message")
    def test_dms_request_with_unexisting_user(self, send_user_message, execute_query, client):
        execute_query.return_value = make_single_application(
            6044787, state=dms_models.GraphQLApplicationStates.draft.value, email="user@example.com"
        )
        form_data = {
            "procedure_id": 48860,
            "dossier_id": 6044787,
            "state": dms_models.GraphQLApplicationStates.draft.value,
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
        assert send_user_message.call_args[0][2] == subscription_messages.DMS_ERROR_MESSAGE_USER_NOT_FOUND

        orphan_dms_application = fraud_models.OrphanDmsApplication.query.filter(
            fraud_models.OrphanDmsApplication.email == "user@example.com"
        ).first()
        assert orphan_dms_application.application_id == 6044787

    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    @patch.object(api_dms.DMSGraphQLClient, "send_user_message")
    def test_dms_request_with_unexisting_user_with_ongoin_application(self, send_user_message, execute_query, client):
        fraud_factories.OrphanDmsApplicationFactory(application_id=6044787, email="user@example.com")
        execute_query.return_value = make_single_application(
            6044787, state=dms_models.GraphQLApplicationStates.on_going.value, email="user@example.com"
        )
        form_data = {
            "procedure_id": 48860,
            "dossier_id": 6044787,
            "state": dms_models.GraphQLApplicationStates.on_going.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # assert an OrphanApplication is not created again
        assert fraud_models.OrphanDmsApplication.query.count() == 1
        # assert the message is not sent again
        assert send_user_message.call_count == 0
        assert len(mails_testing.outbox) == 0

    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_dms_request_with_unexisting_user_with_accepted_application(self, execute_query, client):
        fraud_factories.OrphanDmsApplicationFactory(application_id=6044787, email="user@example.com")
        execute_query.return_value = make_single_application(
            6044787, state=dms_models.GraphQLApplicationStates.accepted.value, email="user@example.com"
        )
        form_data = {
            "procedure_id": 48860,
            "dossier_id": 6044787,
            "state": dms_models.GraphQLApplicationStates.accepted.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # assert an OrphanApplication is not created again
        assert fraud_models.OrphanDmsApplication.query.count() == 1
        # assert an email is sent to ask to create account
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["template"]["id_prod"] == 678

    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    @patch.object(api_dms.DMSGraphQLClient, "send_user_message")
    def test_dms_id_piece_number_error(self, send_user_message, execute_query, client):
        user = users_factories.UserFactory()
        execute_query.return_value = make_single_application(
            12,
            state=dms_models.GraphQLApplicationStates.draft.value,
            email=user.email,
            id_piece_number="error_identity_piece_number",
        )
        form_data = {
            "procedure_id": 48860,
            "dossier_id": 6044787,
            "state": dms_models.GraphQLApplicationStates.draft.value,
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
        assert send_user_message.call_args[0][2] == (
            "Bonjour,\n"
            "\n"
            "Nous avons bien reçu ton dossier, mais il y a une erreur dans le champ contenant ta pièce d'identité, inscrit sur le formulaire en ligne:\n"
            "Ton numéro de pièce d’identité doit être renseigné sous format alphanumérique sans espace et sans caractères spéciaux\n"
            '<a href="https://aide.passculture.app/hc/fr/articles/4411999008657--Jeunes-Où-puis-je-trouver-le-numéro-de-ma-pièce-d-identité">Où puis-je trouver le numéro de ma pièce d’identité ?</a>\n'
            "\n"
            "Merci de corriger ton dossier.\n"
            "\n"
            'Tu trouveras de l’aide dans cet article : <a href="https://aide.passculture.app/hc/fr/articles/4411999116433--Jeunes-Où-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-Démarches-Simplifiées-">Où puis-je trouver de l’aide concernant mon dossier d’inscription sur Démarches Simplifiées ?</a>\n'
            "\n"
            "Nous te souhaitons une belle journée.\n"
            "\n"
            "L’équipe du pass Culture"
        )
        assert len(user.subscriptionMessages) == 1
        assert user.subscriptionMessages[0].popOverIcon == subscription_models.PopOverIcon.WARNING
        assert (
            user.subscriptionMessages[0].userMessage
            == "Il semblerait que le champ ‘ta pièce d'identité’ soit erroné. Tu peux te rendre sur le site Démarches-simplifiées pour le rectifier."
        )

    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    @patch.object(api_dms.DMSGraphQLClient, "send_user_message")
    @testing.override_features(DISABLE_USER_NAME_AND_FIRST_NAME_VALIDATION_IN_TESTING_AND_STAGING=False)
    def test_dms_first_name_error(self, send_user_message, execute_query, client):
        user = users_factories.UserFactory()
        execute_query.return_value = make_single_application(
            12, state=dms_models.GraphQLApplicationStates.draft.value, email=user.email, first_name="first_n@me_error"
        )
        form_data = {
            "procedure_id": 48860,
            "dossier_id": 6044787,
            "state": dms_models.GraphQLApplicationStates.draft.value,
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
        assert send_user_message.call_args[0][2] == (
            "Bonjour,\n"
            "\n"
            "Nous avons bien reçu ton dossier, mais il y a une erreur dans le champ contenant ton prénom, inscrit sur le formulaire en ligne:\n"
            "Merci de corriger ton dossier.\n"
            "\n"
            'Tu trouveras de l’aide dans cet article : <a href="https://aide.passculture.app/hc/fr/articles/4411999116433--Jeunes-Où-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-Démarches-Simplifiées-">Où puis-je trouver de l’aide concernant mon dossier d’inscription sur Démarches Simplifiées ?</a>\n'
            "\n"
            "Nous te souhaitons une belle journée.\n"
            "\n"
            "L’équipe du pass Culture"
        )
        assert len(user.subscriptionMessages) == 1
        assert user.subscriptionMessages[0].popOverIcon == subscription_models.PopOverIcon.WARNING
        assert (
            user.subscriptionMessages[0].userMessage
            == "Il semblerait que le champ ‘ton prénom’ soit erroné. Tu peux te rendre sur le site Démarches-simplifiées pour le rectifier."
        )

    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    @patch.object(api_dms.DMSGraphQLClient, "send_user_message")
    @testing.override_features(DISABLE_USER_NAME_AND_FIRST_NAME_VALIDATION_IN_TESTING_AND_STAGING=False)
    def test_dms_full_name_error(self, send_user_message, execute_query, client):
        user = users_factories.UserFactory()
        execute_query.return_value = make_single_application(
            12,
            state=dms_models.GraphQLApplicationStates.draft.value,
            email=user.email,
            first_name="first_n@me_error",
            last_name="l@st_n@me_error",
        )
        form_data = {
            "procedure_id": 48860,
            "dossier_id": 6044787,
            "state": dms_models.GraphQLApplicationStates.draft.value,
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
        assert send_user_message.call_args[0][2] == (
            "Bonjour,\n"
            "\n"
            "Nous avons bien reçu ton dossier, mais il y a une erreur dans les champs suivants, inscrits sur le formulaire en ligne:\n"
            " - ton prénom\n"
            " - ton nom\n"
            "\n"
            "Pour que ton dossier soit traité, tu dois le modifier en faisant bien attention à remplir correctement toutes les informations.\n"
            "Pour avoir plus d’informations sur les étapes de ton inscription sur Démarches Simplifiées, nous t’invitons à consulter les articles suivants :\n"
            'Jeune de 18 ans : <a href="https://aide.passculture.app/hc/fr/articles/4411991957521--Jeunes-Comment-remplir-le-formulaire-sur-D%C3%A9marches-Simplifi%C3%A9es-">[Jeunes] Comment remplir le formulaire sur Démarches Simplifiées?</a>\n'
            'Jeune de 15 à 17 ans : <a href="https://aide.passculture.app/hc/fr/articles/4404373671324--Jeunes-15-17-ans-Comment-remplir-le-formulaire-sur-D%C3%A9marches-Simplifi%C3%A9es-">[Jeunes 15-17 ans] Comment remplir le formulaire sur Démarches Simplifiées?</a>\n'
            "\n"
            "Merci de corriger ton dossier.\n"
            "\n"
            'Tu trouveras de l’aide dans cet article : <a href="https://aide.passculture.app/hc/fr/articles/4411999116433--Jeunes-Où-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-Démarches-Simplifiées-">Où puis-je trouver de l’aide concernant mon dossier d’inscription sur Démarches Simplifiées ?</a>\n'
            "\n"
            "Nous te souhaitons une belle journée.\n"
            "\n"
            "L’équipe du pass Culture"
        )
        assert len(user.subscriptionMessages) == 1
        assert user.subscriptionMessages[0].popOverIcon == subscription_models.PopOverIcon.WARNING
        assert (
            user.subscriptionMessages[0].userMessage
            == "Il semblerait que les champs ‘ton prénom, ton nom’ soient erronés. Tu peux te rendre sur le site Démarches-simplifiées pour les rectifier."
        )

    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    @patch.object(api_dms.DMSGraphQLClient, "send_user_message")
    def test_dms_postal_code_error(self, send_user_message, execute_query, client):
        user = users_factories.UserFactory()
        execute_query.return_value = make_single_application(
            12, state=dms_models.GraphQLApplicationStates.draft.value, email=user.email, postal_code="error_postal_code"
        )
        form_data = {
            "procedure_id": 48860,
            "dossier_id": 6044787,
            "state": dms_models.GraphQLApplicationStates.draft.value,
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
        assert send_user_message.call_args[0][2] == (
            "Bonjour,\n"
            "\n"
            "Nous avons bien reçu ton dossier, mais il y a une erreur dans le champ contenant ton code postal, inscrit sur le formulaire en ligne:\n"
            "Ton code postal doit être renseigné sous format 5 chiffres uniquement, sans lettre ni espace\n"
            '<a href="https://aide.passculture.app/hc/fr/articles/4411998995985--Jeunes-Comment-bien-renseigner-mon-adresse-et-mon-code-postal-lors-de-l-inscription-">Comment bien renseigner mon adresse et mon code postal lors de l’inscription ? </a>\n'
            "\n"
            "Merci de corriger ton dossier.\n"
            "\n"
            'Tu trouveras de l’aide dans cet article : <a href="https://aide.passculture.app/hc/fr/articles/4411999116433--Jeunes-Où-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-Démarches-Simplifiées-">Où puis-je trouver de l’aide concernant mon dossier d’inscription sur Démarches Simplifiées ?</a>\n'
            "\n"
            "Nous te souhaitons une belle journée.\n"
            "\n"
            "L’équipe du pass Culture"
        )
        assert len(user.subscriptionMessages) == 1
        assert user.subscriptionMessages[0].popOverIcon == subscription_models.PopOverIcon.WARNING
        assert (
            user.subscriptionMessages[0].userMessage
            == "Il semblerait que le champ ‘ton code postal’ soit erroné. Tu peux te rendre sur le site Démarches-simplifiées pour le rectifier."
        )

    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    @patch.object(api_dms.DMSGraphQLClient, "send_user_message")
    @freezegun.freeze_time("2021-12-20 09:00:00")
    @pytest.mark.parametrize("birthday_date", [datetime.date(2012, 5, 12), datetime.date(1999, 6, 12)])
    def test_dms_birth_date_error(self, send_user_message, execute_query, client, birthday_date):
        user = users_factories.UserFactory()
        execute_query.return_value = make_single_application(
            6044787, state=dms_models.GraphQLApplicationStates.draft.value, email=user.email, birth_date=birthday_date
        )

        form_data = {
            "procedure_id": 48860,
            "dossier_id": 6044787,
            "state": dms_models.GraphQLApplicationStates.draft.value,
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
        assert send_user_message.call_args[0][2] == (
            "Bonjour,\n"
            "\n"
            f"Nous avons bien reçu ton dossier, mais la date de naissance que tu as renseignée ({birthday_date}) indique que tu n’as pas l’âge requis pour profiter du pass Culture (tu dois avoir entre 15 et 18 ans).\n"
            f"S’il s’agit d’une erreur, tu peux modifier ton dossier.\n"
            "\n"
            'Tu trouveras de l’aide dans cet article : <a href="https://aide.passculture.app/hc/fr/articles/4411999116433--Jeunes-Où-puis-je-trouver-de-l-aide-concernant-mon-dossier-d-inscription-sur-Démarches-Simplifiées-">Où puis-je trouver de l’aide concernant mon dossier d’inscription sur Démarches Simplifiées ?</a>'
            "\n"
            "Bonne journée,\n"
            "\n"
            "L’équipe du pass Culture"
        )
        assert len(user.subscriptionMessages) == 1
        assert user.subscriptionMessages[0].popOverIcon == subscription_models.PopOverIcon.WARNING
        assert (
            user.subscriptionMessages[0].userMessage
            == "Il semblerait que le champ ‘ta date de naissance’ soit erroné. Tu peux te rendre sur le site Démarches-simplifiées pour le rectifier."
        )

        fraud_check = user.beneficiaryFraudChecks[0]
        assert fraud_check.type == fraud_models.FraudCheckType.DMS
        assert fraud_check.status == fraud_models.FraudCheckStatus.STARTED
        assert fraud_check.reasonCodes == [fraud_models.FraudReasonCode.AGE_NOT_VALID]
        assert (
            fraud_check.reason
            == f"Erreur dans les données soumises dans le dossier DMS : 'birth_date' ({birthday_date.isoformat()})"
        )

    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_dms_application_on_going(self, execute_query, client):
        user = users_factories.UserFactory()
        execute_query.return_value = make_single_application(
            12, state=dms_models.GraphQLApplicationStates.on_going.value, email=user.email
        )

        form_data = {
            "procedure_id": 48860,
            "dossier_id": 6044787,
            "state": dms_models.GraphQLApplicationStates.on_going.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }

        response = client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 204

        assert user.beneficiaryFraudChecks[0].status == fraud_models.FraudCheckStatus.PENDING
        assert user.beneficiaryFraudChecks[0].type == fraud_models.FraudCheckType.DMS
        assert user.beneficiaryFraudChecks[0].eligibilityType == users_models.EligibilityType.AGE18

        assert fraud_api.has_user_performed_identity_check(user)

    @patch.object(api_dms.DMSGraphQLClient, "execute_query")
    def test_dms_field_error_then_corrected(self, execute_query, client):
        user = users_factories.UserFactory()
        execute_query.return_value = make_single_application(
            12,
            state=dms_models.GraphQLApplicationStates.draft.value,
            email=user.email,
            id_piece_number="error_identity_piece_number",
            last_modification_date=datetime.datetime(2021, 9, 30, 17, 55, 58),
        )
        form_data = {
            "procedure_id": 48860,
            "dossier_id": 6044787,
            "state": dms_models.GraphQLApplicationStates.on_going.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }

        # First DMS webhook call: draft with value errors
        response = client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        fraud_check = user.beneficiaryFraudChecks[0]

        assert response.status_code == 204
        assert execute_query.call_count == 2  # 1 to fetch application, 1 to send user message
        assert fraud_check.type == fraud_models.FraudCheckType.DMS
        assert fraud_check.status == fraud_models.FraudCheckStatus.STARTED
        assert fraud_check.reasonCodes == [fraud_models.FraudReasonCode.ERROR_IN_DATA]

        # Second DMS webhook call: on_going with no value errors
        execute_query.reset_mock()
        execute_query.return_value = make_single_application(
            12,
            state=dms_models.GraphQLApplicationStates.on_going.value,
            email=user.email,
            last_modification_date=datetime.datetime(2021, 9, 30, 18, 00, 00),
        )
        response = client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 204
        assert execute_query.call_count == 1
        assert fraud_check.type == fraud_models.FraudCheckType.DMS
        assert fraud_check.status == fraud_models.FraudCheckStatus.PENDING


@pytest.mark.usefixtures("db_session")
class UbbleWebhookTest:
    def _get_request_body(self, fraud_check, status) -> ubble_routes.WebhookRequest:
        return ubble_routes.WebhookRequest(
            identification_id=fraud_check.thirdPartyId,
            status=status,
            configuration=ubble_routes.Configuration(
                id=fraud_check.user.id,
                name="Pass Culture",
            ),
        )

    def _get_signature(self, payload):
        timestamp = str(int(time.time()))
        token = ubble_routes.compute_signature(timestamp.encode("utf-8"), payload.encode("utf-8"))
        return f"ts={timestamp},v1={token}"

    def _init_test(self, current_identification_state, notified_identification_state):
        user = users_factories.UserFactory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            dateOfBirth=datetime.datetime.utcnow() - relativedelta.relativedelta(years=18),
            activity="Lycéen",
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.HONOR_STATEMENT, user=user, status=fraud_models.FraudCheckStatus.OK
        )
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            resultContent=fraud_factories.UbbleContentFactory(
                status=test_factories.STATE_STATUS_MAPPING[current_identification_state].value,
            ),
            user=user,
            status=fraud_models.FraudCheckStatus.STARTED,
        )
        request_data = self._get_request_body(
            fraud_check, test_factories.STATE_STATUS_MAPPING[notified_identification_state]
        )
        payload = json.dumps(request_data.dict(by_alias=True), default=json_default)
        ubble_identification_response = test_factories.UbbleIdentificationResponseFactory(
            identification_state=notified_identification_state,
            data__attributes__identification_id=str(request_data.identification_id),
        )
        return payload, request_data, ubble_identification_response

    def test_webhook_signature_ok(self, client, ubble_mocker):
        current_identification_state = test_factories.IdentificationState.INITIATED
        notified_identification_state = test_factories.IdentificationState.PROCESSING
        _, request_data, ubble_identification_response = self._init_test(
            current_identification_state, notified_identification_state
        )

        response = self._post_webhook(client, ubble_mocker, request_data, ubble_identification_response)

        assert response.status_code == 200
        assert response.json == {"status": "ok"}

    def test_webhook_signature_bad(self, client, ubble_mocker):
        current_identification_state = test_factories.IdentificationState.INITIATED
        notified_identification_state = test_factories.IdentificationState.PROCESSING
        payload, request_data, ubble_identification_response = self._init_test(
            current_identification_state, notified_identification_state
        )

        with ubble_mocker(
            request_data.identification_id,
            json.dumps(ubble_identification_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            response = client.post(
                "/webhooks/ubble/application_status",
                headers={"Ubble-Signature": "bad_signature"},
                raw_json=payload,
            )

        assert response.status_code == 403
        assert response.json == {"signature": ["Invalid signature"]}

    def test_webhook_signature_missing(self, client, ubble_mocker):
        current_identification_state = test_factories.IdentificationState.INITIATED
        notified_identification_state = test_factories.IdentificationState.PROCESSING
        payload, request_data, ubble_identification_response = self._init_test(
            current_identification_state, notified_identification_state
        )

        with ubble_mocker(
            request_data.identification_id,
            json.dumps(ubble_identification_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            response = client.post(
                "/webhooks/ubble/application_status",
                raw_json=payload,
            )

        assert response.status_code == 403
        assert response.json == {"signature": ["Invalid signature"]}

    def test_exception_during_workflow_update(self, client):
        current_identification_state = test_factories.IdentificationState.INITIATED
        notified_identification_state = test_factories.IdentificationState.PROCESSING
        payload, _, _ = self._init_test(current_identification_state, notified_identification_state)
        signature = self._get_signature(payload)

        with mock.patch(
            "pcapi.core.subscription.ubble.api.update_ubble_workflow",
            side_effect=Exception(),
        ):
            response = client.post(
                "/webhooks/ubble/application_status",
                headers={"Ubble-Signature": signature},
                raw_json=payload,
            )

        assert response.status_code == 500
        assert response.json == {"msg": "an error occured during workflow update"}

    def test_fraud_check_initiated(self, client, ubble_mocker):
        current_identification_state = test_factories.IdentificationState.NEW
        notified_identification_state = test_factories.IdentificationState.INITIATED
        _, request_data, ubble_identification_response = self._init_test(
            current_identification_state, notified_identification_state
        )

        self._post_webhook(client, ubble_mocker, request_data, ubble_identification_response)

        fraud_check = ubble_fraud_api.get_ubble_fraud_check(
            ubble_identification_response.data.attributes.identification_id
        )
        assert fraud_check.reason is None
        assert fraud_check.reasonCodes is None
        assert fraud_check.status is fraud_models.FraudCheckStatus.STARTED
        assert fraud_check.type == fraud_models.FraudCheckType.UBBLE
        assert fraud_check.thirdPartyId == ubble_identification_response.data.attributes.identification_id
        content = ubble_fraud_models.UbbleContent(**fraud_check.resultContent)
        assert content.score is None
        assert content.status == test_factories.STATE_STATUS_MAPPING[notified_identification_state]
        assert content.comment is None
        assert content.last_name is None
        assert content.first_name is None
        assert content.birth_date is None
        assert content.supported is None
        assert content.document_type is None
        assert content.expiry_date_score is None
        assert content.id_document_number is None
        assert str(content.identification_id) == ubble_identification_response.data.attributes.identification_id
        assert (
            content.identification_url == f"{settings.UBBLE_API_URL}/identifications/{str(content.identification_id)}"
        )

    def test_fraud_check_aborted(self, client, ubble_mocker):
        current_identification_state = test_factories.IdentificationState.INITIATED
        notified_identification_state = test_factories.IdentificationState.ABORTED
        _, request_data, ubble_identification_response = self._init_test(
            current_identification_state, notified_identification_state
        )

        self._post_webhook(client, ubble_mocker, request_data, ubble_identification_response)

        fraud_check = ubble_fraud_api.get_ubble_fraud_check(
            ubble_identification_response.data.attributes.identification_id
        )
        assert fraud_check.reason is None
        assert fraud_check.reasonCodes is None
        assert fraud_check.status is fraud_models.FraudCheckStatus.CANCELED
        assert fraud_check.type == fraud_models.FraudCheckType.UBBLE
        assert fraud_check.thirdPartyId == ubble_identification_response.data.attributes.identification_id
        content = ubble_fraud_models.UbbleContent(**fraud_check.resultContent)
        assert content.score is None
        assert content.status == test_factories.STATE_STATUS_MAPPING[notified_identification_state]
        assert content.comment is None
        assert content.last_name is None
        assert content.first_name is None
        assert content.birth_date is None
        assert content.supported is None
        assert content.document_type is None
        assert content.expiry_date_score is None
        assert str(content.identification_id) == ubble_identification_response.data.attributes.identification_id
        assert content.id_document_number is None
        assert (
            content.identification_url == f"{settings.UBBLE_API_URL}/identifications/{str(content.identification_id)}"
        )

    def test_fraud_check_processing(self, client, ubble_mocker):
        current_identification_state = test_factories.IdentificationState.INITIATED
        notified_identification_state = test_factories.IdentificationState.PROCESSING
        _, request_data, ubble_identification_response = self._init_test(
            current_identification_state, notified_identification_state
        )

        self._post_webhook(client, ubble_mocker, request_data, ubble_identification_response)

        fraud_check = ubble_fraud_api.get_ubble_fraud_check(
            ubble_identification_response.data.attributes.identification_id
        )
        assert fraud_check.reason is None
        assert fraud_check.reasonCodes is None
        assert fraud_check.status is fraud_models.FraudCheckStatus.PENDING
        assert fraud_check.type == fraud_models.FraudCheckType.UBBLE
        assert fraud_check.thirdPartyId == ubble_identification_response.data.attributes.identification_id
        assert (
            subscription_api.get_identity_check_subscription_status(fraud_check.user, fraud_check.user.eligibility)
            == subscription_models.SubscriptionItemStatus.PENDING
        )
        content = ubble_fraud_models.UbbleContent(**fraud_check.resultContent)
        document = list(filter(lambda included: included.type == "documents", ubble_identification_response.included))[
            0
        ].attributes
        assert content.score is None
        assert content.status == test_factories.STATE_STATUS_MAPPING[notified_identification_state]
        assert content.comment == ubble_identification_response.data.attributes.comment
        assert content.last_name == document.last_name
        assert content.first_name == document.first_name
        assert str(content.birth_date) == document.birth_date
        assert content.supported is None
        assert content.document_type == document.document_type
        assert content.expiry_date_score is None
        assert str(content.identification_id) == ubble_identification_response.data.attributes.identification_id
        assert content.id_document_number == document.document_number
        assert (
            content.identification_url == f"{settings.UBBLE_API_URL}/identifications/{str(content.identification_id)}"
        )

    def test_fraud_check_valid(self, client, ubble_mocker, mocker):
        current_identification_state = test_factories.IdentificationState.PROCESSING
        notified_identification_state = test_factories.IdentificationState.VALID
        _, request_data, ubble_identification_response = self._init_test(
            current_identification_state, notified_identification_state
        )

        self._post_webhook(client, ubble_mocker, request_data, ubble_identification_response)

        fraud_check = ubble_fraud_api.get_ubble_fraud_check(
            ubble_identification_response.data.attributes.identification_id
        )
        assert fraud_check.reason == ""
        assert fraud_check.reasonCodes == []
        assert fraud_check.status is fraud_models.FraudCheckStatus.OK
        assert fraud_check.type == fraud_models.FraudCheckType.UBBLE
        assert fraud_check.thirdPartyId == ubble_identification_response.data.attributes.identification_id

        assert fraud_check.user.has_beneficiary_role
        assert len(fraud_check.user.deposits) == 1

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["To"] == fraud_check.user.email

        content = ubble_fraud_models.UbbleContent(**fraud_check.resultContent)
        document = list(filter(lambda included: included.type == "documents", ubble_identification_response.included))[
            0
        ].attributes
        assert content.score == ubble_fraud_models.UbbleScore.VALID.value
        assert content.status == test_factories.STATE_STATUS_MAPPING[notified_identification_state]
        assert content.comment == ubble_identification_response.data.attributes.comment
        assert content.last_name == document.last_name
        assert content.first_name == document.first_name
        assert str(content.birth_date) == document.birth_date
        assert content.supported == ubble_fraud_models.UbbleScore.VALID.value
        assert content.document_type == document.document_type
        assert content.expiry_date_score == ubble_fraud_models.UbbleScore.VALID.value
        assert str(content.identification_id) == ubble_identification_response.data.attributes.identification_id
        assert content.id_document_number == document.document_number
        assert (
            content.identification_url == f"{settings.UBBLE_API_URL}/identifications/{str(content.identification_id)}"
        )

        # Ensure that user information has been updated with Ubble extracted data
        assert fraud_check.user.firstName == document.first_name
        assert fraud_check.user.lastName == document.last_name
        assert fraud_check.user.dateOfBirth.date().isoformat() == document.birth_date
        assert fraud_check.user.idPieceNumber == document.document_number

    def test_fraud_check_invalid(self, client, ubble_mocker, mocker):
        current_identification_state = test_factories.IdentificationState.PROCESSING
        notified_identification_state = test_factories.IdentificationState.INVALID
        _, request_data, ubble_identification_response = self._init_test(
            current_identification_state, notified_identification_state
        )

        self._post_webhook(client, ubble_mocker, request_data, ubble_identification_response)

        fraud_check = ubble_fraud_api.get_ubble_fraud_check(
            ubble_identification_response.data.attributes.identification_id
        )
        assert fraud_check.reason is not None
        assert fraud_check.reasonCodes is not None
        assert fraud_check.status is fraud_models.FraudCheckStatus.KO
        assert fraud_check.type == fraud_models.FraudCheckType.UBBLE
        assert fraud_check.thirdPartyId == ubble_identification_response.data.attributes.identification_id

        assert not fraud_check.user.has_beneficiary_role
        assert len(fraud_check.user.deposits) == 0

        assert len(mails_testing.outbox) == 0

        content = ubble_fraud_models.UbbleContent(**fraud_check.resultContent)
        document = list(filter(lambda included: included.type == "documents", ubble_identification_response.included))[
            0
        ].attributes
        document_check = list(
            filter(lambda included: included.type == "document-checks", ubble_identification_response.included)
        )[0].attributes
        assert content.score == ubble_fraud_models.UbbleScore.INVALID.value
        assert content.status == test_factories.STATE_STATUS_MAPPING[notified_identification_state]
        assert content.comment == ubble_identification_response.data.attributes.comment
        assert content.last_name == document.last_name
        assert content.first_name == document.first_name
        assert str(content.birth_date) == document.birth_date
        assert content.supported == document_check.supported
        assert content.document_type == document.document_type
        assert content.expiry_date_score == document_check.expiry_date_score
        assert str(content.identification_id) == ubble_identification_response.data.attributes.identification_id
        assert content.id_document_number == document.document_number
        assert (
            content.identification_url == f"{settings.UBBLE_API_URL}/identifications/{str(content.identification_id)}"
        )

    def test_fraud_check_unprocessable(self, client, ubble_mocker, mocker):
        current_identification_state = test_factories.IdentificationState.PROCESSING
        notified_identification_state = test_factories.IdentificationState.UNPROCESSABLE
        _, request_data, ubble_identification_response = self._init_test(
            current_identification_state, notified_identification_state
        )

        self._post_webhook(client, ubble_mocker, request_data, ubble_identification_response)

        fraud_check = ubble_fraud_api.get_ubble_fraud_check(
            ubble_identification_response.data.attributes.identification_id
        )
        assert fraud_check.reason == "Ubble score UNDECIDABLE: None | Ubble n'a pas réussi à lire le document"
        assert fraud_check.reasonCodes == [fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE]
        assert fraud_check.status is fraud_models.FraudCheckStatus.SUSPICIOUS
        assert fraud_check.type == fraud_models.FraudCheckType.UBBLE
        assert fraud_check.thirdPartyId == ubble_identification_response.data.attributes.identification_id

        assert not fraud_check.user.has_beneficiary_role
        assert len(fraud_check.user.deposits) == 0

        self._assert_email_sent(fraud_check.user, 304)

        content = ubble_fraud_models.UbbleContent(**fraud_check.resultContent)
        document = list(filter(lambda included: included.type == "documents", ubble_identification_response.included))[
            0
        ].attributes
        document_check = list(
            filter(lambda included: included.type == "document-checks", ubble_identification_response.included)
        )[0].attributes
        assert content.score == ubble_fraud_models.UbbleScore.UNDECIDABLE.value
        assert content.status == test_factories.STATE_STATUS_MAPPING[notified_identification_state]
        assert content.comment == ubble_identification_response.data.attributes.comment
        assert content.last_name == document.last_name
        assert content.first_name == document.first_name
        assert str(content.birth_date == document.birth_date)
        assert content.supported == document_check.supported
        assert content.document_type == document.document_type
        assert content.expiry_date_score == document_check.expiry_date_score
        assert str(content.identification_id) == ubble_identification_response.data.attributes.identification_id
        assert content.id_document_number == document.document_number
        assert (
            content.identification_url == f"{settings.UBBLE_API_URL}/identifications/{str(content.identification_id)}"
        )

    def test_fraud_check_already_finished(self, client, ubble_mocker):
        current_identification_state = test_factories.IdentificationState.VALID
        notified_identification_state = test_factories.IdentificationState.VALID
        _, request_data, ubble_identification_response = self._init_test(
            current_identification_state, notified_identification_state
        )
        fraud_check = ubble_fraud_api.get_ubble_fraud_check(
            ubble_identification_response.data.attributes.identification_id
        )
        fraud_check.status = fraud_models.FraudCheckStatus.OK
        fraud_check.user.roles = [users_models.UserRole.BENEFICIARY]
        repository.save(fraud_check)

        response = self._post_webhook(client, ubble_mocker, request_data, ubble_identification_response)

        assert response.status_code == 200
        assert fraud_check.status == fraud_models.FraudCheckStatus.OK

    def test_birth_date_overrided_with_ubble_test_emails(self, client, ubble_mocker, mocker):
        email = "whatever+ubble_test@example.com"
        subscription_birth_date = datetime.datetime.combine(
            datetime.date.today(), datetime.time(0, 0)
        ) - relativedelta.relativedelta(years=18, months=6)
        document_birth_date = datetime.datetime.combine(
            datetime.date.today(), datetime.time(0, 0)
        ) - relativedelta.relativedelta(years=28)
        user = users_factories.UserFactory(
            email=email,
            dateOfBirth=subscription_birth_date,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            activity="Lycéen",
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=fraud_models.FraudCheckStatus.OK,
        )
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            resultContent=fraud_factories.UbbleContentFactory(
                status=test_factories.STATE_STATUS_MAPPING[test_factories.IdentificationState.PROCESSING].value,
            ),
            user=user,
            status=fraud_models.FraudCheckStatus.PENDING,
            reason=None,
            reasonCodes=None,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        request_data = self._get_request_body(fraud_check, ubble_fraud_models.UbbleIdentificationStatus.PROCESSED)
        ubble_identification_response = test_factories.UbbleIdentificationResponseFactory(
            identification_state=test_factories.IdentificationState.VALID,
            data__attributes__identification_id=str(request_data.identification_id),
            included=[
                test_factories.UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=document_birth_date.date().isoformat()
                ),
                test_factories.UbbleIdentificationIncludedDocumentChecksFactory(),
            ],
        )

        self._post_webhook(client, ubble_mocker, request_data, ubble_identification_response)

        db.session.refresh(user)
        db.session.refresh(fraud_check)
        assert fraud_check.source_data().birth_date != document_birth_date.date()
        assert fraud_check.source_data().birth_date == subscription_birth_date.date()
        assert user.has_beneficiary_role is True
        assert fraud_check.status == fraud_models.FraudCheckStatus.OK

    def test_birth_date_not_overridden_with_non_ubble_test_emails(self, client, ubble_mocker, mocker):
        email = "whatever@example.com"
        subscription_birth_date = datetime.datetime.combine(
            datetime.date.today(), datetime.time(0, 0)
        ) - relativedelta.relativedelta(years=18, months=6)
        document_birth_date = datetime.datetime.combine(
            datetime.date.today(), datetime.time(0, 0)
        ) - relativedelta.relativedelta(years=28)
        user = users_factories.UserFactory(email=email, dateOfBirth=subscription_birth_date)
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            resultContent=fraud_factories.UbbleContentFactory(
                status=test_factories.STATE_STATUS_MAPPING[test_factories.IdentificationState.PROCESSING].value,
            ),
            user=user,
            status=fraud_models.FraudCheckStatus.PENDING,
            reason=None,
            reasonCodes=None,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        request_data = self._get_request_body(fraud_check, ubble_fraud_models.UbbleIdentificationStatus.PROCESSED)
        ubble_identification_response = test_factories.UbbleIdentificationResponseFactory(
            identification_state=test_factories.IdentificationState.VALID,
            data__attributes__identification_id=str(request_data.identification_id),
            included=[
                test_factories.UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=document_birth_date.date().isoformat()
                ),
                test_factories.UbbleIdentificationIncludedDocumentChecksFactory(),
            ],
        )

        self._post_webhook(client, ubble_mocker, request_data, ubble_identification_response)

        db.session.refresh(user)
        db.session.refresh(fraud_check)
        assert fraud_check.source_data().birth_date == document_birth_date.date()
        assert fraud_check.source_data().birth_date != subscription_birth_date.date()
        assert user.has_beneficiary_role is False
        assert fraud_check.status == fraud_models.FraudCheckStatus.KO

    @testing.override_settings(IS_PROD=True)
    def test_ubble_test_emails_not_actives_on_production(self, client, ubble_mocker, mocker):
        email = "whatever+ubble_test@example.com"
        subscription_birth_date = datetime.datetime.combine(
            datetime.date.today(), datetime.time(0, 0)
        ) - relativedelta.relativedelta(years=18, months=6)
        document_birth_date = datetime.datetime.combine(
            datetime.date.today(), datetime.time(0, 0)
        ) - relativedelta.relativedelta(years=28)
        user = users_factories.UserFactory(email=email, dateOfBirth=subscription_birth_date)
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            resultContent=fraud_factories.UbbleContentFactory(
                status=test_factories.STATE_STATUS_MAPPING[test_factories.IdentificationState.PROCESSING].value,
            ),
            user=user,
            status=fraud_models.FraudCheckStatus.PENDING,
            reason=None,
            reasonCodes=None,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        request_data = self._get_request_body(fraud_check, ubble_fraud_models.UbbleIdentificationStatus.PROCESSED)
        ubble_identification_response = test_factories.UbbleIdentificationResponseFactory(
            identification_state=test_factories.IdentificationState.VALID,
            data__attributes__identification_id=str(request_data.identification_id),
            included=[
                test_factories.UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=document_birth_date.date().isoformat()
                ),
                test_factories.UbbleIdentificationIncludedDocumentChecksFactory(),
            ],
        )

        self._post_webhook(client, ubble_mocker, request_data, ubble_identification_response)

        db.session.refresh(user)
        db.session.refresh(fraud_check)
        assert fraud_check.source_data().birth_date == document_birth_date.date()
        assert fraud_check.source_data().birth_date != subscription_birth_date.date()
        assert user.has_beneficiary_role is False
        assert fraud_check.status == fraud_models.FraudCheckStatus.KO

    def _init_decision_test(
        self,
    ) -> typing.Tuple[users_models.User, fraud_models.BeneficiaryFraudCheck, ubble_routes.WebhookRequest]:
        birth_date = datetime.datetime.utcnow().date() - relativedelta.relativedelta(years=18, months=6)
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.combine(birth_date, datetime.time(0, 0)))
        profiling_fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent={},
            status=fraud_models.FraudCheckStatus.OK,
            reason=None,
            reasonCodes=None,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        repository.save(profiling_fraud_check)
        identification_id = str(uuid.uuid4())
        ubble_fraud_check = fraud_models.BeneficiaryFraudCheck(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            thirdPartyId=identification_id,
            resultContent={
                "birth_date": None,
                "comment": "",
                "document_type": None,
                "expiry_date_score": None,
                "first_name": None,
                "id_document_number": None,
                "identification_id": identification_id,
                "identification_url": f"https://id.ubble.ai/{identification_id}",
                "last_name": None,
                "registration_datetime": datetime.datetime.utcnow().isoformat(),
                "score": None,
                "status": ubble_fraud_models.UbbleIdentificationStatus.PROCESSING.value,
                "supported": None,
            },
            status=fraud_models.FraudCheckStatus.PENDING,
            reason=None,
            reasonCodes=None,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        repository.save(ubble_fraud_check)
        honor_fraud_check = fraud_models.BeneficiaryFraudCheck(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            thirdPartyId="internal_check_4483",
            resultContent=None,
            status=fraud_models.FraudCheckStatus.OK,
            reason=None,
            reasonCodes=None,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        repository.save(honor_fraud_check)
        request_data = self._get_request_body(ubble_fraud_check, ubble_fraud_models.UbbleIdentificationStatus.PROCESSED)
        return user, ubble_fraud_check, request_data

    def _post_webhook(self, client, ubble_mocker, request_data, ubble_identification_response):
        payload = json.dumps(request_data.dict(by_alias=True), default=json_default)
        signature = self._get_signature(payload)

        with ubble_mocker(
            request_data.identification_id,
            json.dumps(ubble_identification_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            return client.post(
                "/webhooks/ubble/application_status",
                headers={"Ubble-Signature": signature},
                raw_json=payload,
            )

    def _log_for_debug(self, user, ubble_fraud_check):
        logging.warning("%s", user)
        logging.warning("  - roles: %s", user.roles)
        logging.warning("  - deposit: %s", user.deposit)
        logging.warning("%s", ubble_fraud_check)
        logging.warning("  - status: %s", ubble_fraud_check.status)
        logging.warning("  - reason: %s", ubble_fraud_check.reason)
        logging.warning("  - reasonCodes: %s", ubble_fraud_check.reasonCodes)
        logging.warning("  - resultContent: %s", ubble_fraud_check.resultContent)

    def _assert_email_sent(self, user, id_prod):
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["template"]["id_prod"] == id_prod
        assert mails_testing.outbox[0].sent_data["To"] == user.email

    @pytest.mark.parametrize(
        "age,reason_code,reason,inappmessage",
        [
            (
                14,
                fraud_models.FraudReasonCode.AGE_TOO_YOUNG,
                "L'utilisateur n'a pas encore l'âge requis (14 ans)",
                "Ton dossier a été bloqué : Tu n'as pas encore l'âge pour bénéficier du pass Culture. Reviens à tes 15 ans pour profiter de ton crédit.",
            ),
            (
                19,
                fraud_models.FraudReasonCode.AGE_TOO_OLD,
                "L'utilisateur a dépassé l'âge maximum (19 ans)",
                "Ton dossier a été bloqué : Tu ne peux pas bénéficier du pass Culture. Il est réservé aux jeunes de 15 à 18 ans.",
            ),
            (
                28,
                fraud_models.FraudReasonCode.AGE_TOO_OLD,
                "L'utilisateur a dépassé l'âge maximum (28 ans)",
                "Ton dossier a été bloqué : Tu ne peux pas bénéficier du pass Culture. Il est réservé aux jeunes de 15 à 18 ans.",
            ),
        ],
    )
    def test_decision_age_cannot_become_beneficiary(self, client, ubble_mocker, age, reason_code, reason, inappmessage):
        document_birth_date = datetime.datetime.utcnow().date() - relativedelta.relativedelta(years=age)
        user, ubble_fraud_check, request_data = self._init_decision_test()

        request_data = self._get_request_body(ubble_fraud_check, ubble_fraud_models.UbbleIdentificationStatus.PROCESSED)
        ubble_identification_response = test_factories.UbbleIdentificationResponseFactory(
            identification_state=test_factories.IdentificationState.VALID,
            data__attributes__identification_id=str(request_data.identification_id),
            included=[
                test_factories.UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=document_birth_date.isoformat(),
                    attributes__document_number="012345678910",
                    attributes__document_type="CI",
                    attributes__first_name=user.firstName,
                    attributes__last_name=user.lastName,
                ),
                test_factories.UbbleIdentificationIncludedDocumentChecksFactory(
                    attributes__data_extracted_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__expiry_date_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__issue_date_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__live_video_capture_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__mrz_validity_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__mrz_viz_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_back_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_front_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__quality_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__visual_back_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__visual_front_score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedFaceChecksFactory(
                    attributes__active_liveness_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__live_video_capture_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__quality_score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedDocFaceMatchesFactory(
                    attributes__score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedReferenceDataChecksFactory(
                    attributes__score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
            ],
        )

        self._post_webhook(client, ubble_mocker, request_data, ubble_identification_response)

        db.session.refresh(user)
        db.session.refresh(ubble_fraud_check)
        self._log_for_debug(user, ubble_fraud_check)

        assert not user.has_beneficiary_role

        assert ubble_fraud_check.status == fraud_models.FraudCheckStatus.KO
        assert reason_code in ubble_fraud_check.reasonCodes
        assert reason in [s.strip() for s in ubble_fraud_check.reason.split(";")]

        assert not ubble_fraud_api.is_user_allowed_to_perform_ubble_check(user, user.eligibility)  # no retry

        message = subscription_models.SubscriptionMessage.query.one()
        assert message.userMessage == inappmessage
        assert message.popOverIcon == subscription_models.PopOverIcon.ERROR

        assert len(mails_testing.outbox) == 0

    def test_decision_duplicate_user(self, client, ubble_mocker):
        birth_date = datetime.datetime.utcnow().date() - relativedelta.relativedelta(years=18, months=2)
        existing_user = users_factories.BeneficiaryGrant18Factory(
            firstName="Duplicate",
            lastName="Fraudster",
            dateOfBirth=datetime.datetime.combine(birth_date, datetime.time(0, 0)),
            email="shotgun@me.com",
        )

        user, ubble_fraud_check, request_data = self._init_decision_test()

        ubble_identification_response = test_factories.UbbleIdentificationResponseFactory(
            identification_state=test_factories.IdentificationState.VALID,
            data__attributes__identification_id=str(request_data.identification_id),
            included=[
                test_factories.UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=existing_user.dateOfBirth.date().isoformat(),
                    attributes__document_number="012345678910",
                    attributes__document_type="CI",
                    attributes__first_name=existing_user.firstName,
                    attributes__last_name=existing_user.lastName,
                ),
                test_factories.UbbleIdentificationIncludedDocumentChecksFactory(
                    attributes__data_extracted_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__expiry_date_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__issue_date_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__live_video_capture_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__mrz_validity_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__mrz_viz_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_back_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_front_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__quality_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__visual_back_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__visual_front_score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedFaceChecksFactory(
                    attributes__active_liveness_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__live_video_capture_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__quality_score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedDocFaceMatchesFactory(
                    attributes__score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedReferenceDataChecksFactory(
                    attributes__score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
            ],
        )

        self._post_webhook(client, ubble_mocker, request_data, ubble_identification_response)

        db.session.refresh(user)
        db.session.refresh(ubble_fraud_check)
        self._log_for_debug(user, ubble_fraud_check)

        assert not user.has_beneficiary_role
        assert ubble_fraud_check.status == fraud_models.FraudCheckStatus.SUSPICIOUS
        assert fraud_models.FraudReasonCode.DUPLICATE_USER in ubble_fraud_check.reasonCodes

        assert not ubble_fraud_api.is_user_allowed_to_perform_ubble_check(user, user.eligibility)  # no retry

        message = subscription_models.SubscriptionMessage.query.one()
        assert (
            message.userMessage
            == "Ton dossier a été bloqué : Il y a déjà un compte à ton nom sur le pass Culture. Tu peux contacter le support pour plus d'informations."
        )
        assert (
            message.callToActionLink
            == subscription_messages.MAILTO_SUPPORT + subscription_messages.MAILTO_SUPPORT_PARAMS.format(id=user.id)
        )
        assert message.callToActionIcon == subscription_models.CallToActionIcon.EMAIL
        assert message.callToActionTitle == "Contacter le support"

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["params"] == {"DUPLICATE_BENEFICIARY_EMAIL": "sho***@me.com"}

    def test_decision_duplicate_id_piece_number(self, client, ubble_mocker):
        users_factories.BeneficiaryGrant18Factory(
            dateOfBirth=datetime.datetime.utcnow().date() - relativedelta.relativedelta(years=18, months=2),
            idPieceNumber="012345678910",
            email="prems@me.com",
        )

        user, ubble_fraud_check, request_data = self._init_decision_test()

        ubble_identification_response = test_factories.UbbleIdentificationResponseFactory(
            identification_state=test_factories.IdentificationState.VALID,
            data__attributes__identification_id=str(request_data.identification_id),
            included=[
                test_factories.UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=(
                        datetime.datetime.utcnow().date() - relativedelta.relativedelta(years=18, months=1)
                    ).isoformat(),
                    attributes__document_number="012345678910",
                    attributes__document_type="CI",
                    attributes__first_name="John",
                    attributes__last_name="Doe",
                ),
                test_factories.UbbleIdentificationIncludedDocumentChecksFactory(
                    attributes__data_extracted_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__expiry_date_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__issue_date_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__live_video_capture_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__mrz_validity_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__mrz_viz_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_back_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_front_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__quality_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__visual_back_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__visual_front_score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedFaceChecksFactory(
                    attributes__active_liveness_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__live_video_capture_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__quality_score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedDocFaceMatchesFactory(
                    attributes__score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedReferenceDataChecksFactory(
                    attributes__score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
            ],
        )

        self._post_webhook(client, ubble_mocker, request_data, ubble_identification_response)

        db.session.refresh(user)
        db.session.refresh(ubble_fraud_check)
        self._log_for_debug(user, ubble_fraud_check)

        assert ubble_fraud_check.status == fraud_models.FraudCheckStatus.SUSPICIOUS
        assert fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER in ubble_fraud_check.reasonCodes

        assert not ubble_fraud_api.is_user_allowed_to_perform_ubble_check(user, user.eligibility)  # no retry

        message = subscription_models.SubscriptionMessage.query.one()
        assert (
            message.userMessage
            == "Ton dossier a été bloqué : Il y a déjà un compte à ton nom sur le pass Culture. Tu peux contacter le support pour plus d'informations."
        )
        assert (
            message.callToActionLink
            == subscription_messages.MAILTO_SUPPORT + subscription_messages.MAILTO_SUPPORT_PARAMS.format(id=user.id)
        )
        assert message.callToActionIcon == subscription_models.CallToActionIcon.EMAIL
        assert message.callToActionTitle == "Contacter le support"

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["params"] == {"DUPLICATE_BENEFICIARY_EMAIL": "pre***@me.com"}

        assert not user.has_beneficiary_role

    def test_decision_reference_data_check_failed(self, client, ubble_mocker):
        user, ubble_fraud_check, request_data = self._init_decision_test()

        ubble_identification_response = test_factories.UbbleIdentificationResponseFactory(
            identification_state=test_factories.IdentificationState.INVALID,  # 0
            data__attributes__identification_id=str(request_data.identification_id),
            included=[
                test_factories.UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=user.dateOfBirth.date().isoformat(),
                    attributes__document_number="012345678910",
                    attributes__document_type="CI",
                    attributes__first_name="FRAUDSTER",
                    attributes__last_name="FRAUDSTER",
                ),
                test_factories.UbbleIdentificationIncludedDocumentChecksFactory(
                    attributes__supported=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__data_extracted_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__expiry_date_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__issue_date_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__live_video_capture_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__mrz_validity_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__mrz_viz_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_back_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_front_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__quality_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__visual_back_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__visual_front_score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedFaceChecksFactory(
                    attributes__active_liveness_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__live_video_capture_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__quality_score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedDocFaceMatchesFactory(
                    attributes__score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedReferenceDataChecksFactory(
                    attributes__score=ubble_fraud_models.UbbleScore.INVALID.value,  # 0
                ),
            ],
        )

        self._post_webhook(client, ubble_mocker, request_data, ubble_identification_response)

        db.session.refresh(user)
        db.session.refresh(ubble_fraud_check)
        self._log_for_debug(user, ubble_fraud_check)

        assert not user.has_beneficiary_role
        assert ubble_fraud_check.status == fraud_models.FraudCheckStatus.SUSPICIOUS
        assert fraud_models.FraudReasonCode.ID_CHECK_DATA_MATCH in ubble_fraud_check.reasonCodes

        assert not ubble_fraud_api.is_user_allowed_to_perform_ubble_check(user, user.eligibility)  # no retry

        message = subscription_models.SubscriptionMessage.query.one()
        assert (
            message.userMessage
            == "Ton dossier a été bloqué : Les informations que tu as renseignées ne correspondent pas à celles de ta pièce d'identité. Tu peux contacter le support pour plus d'informations."
        )
        assert (
            message.callToActionLink
            == subscription_messages.MAILTO_SUPPORT + subscription_messages.MAILTO_SUPPORT_PARAMS.format(id=user.id)
        )
        assert message.callToActionIcon == subscription_models.CallToActionIcon.EMAIL
        assert message.callToActionTitle == "Contacter le support"

        self._assert_email_sent(user, 410)

    @pytest.mark.parametrize(
        "ref_data_check_score",
        [ubble_fraud_models.UbbleScore.VALID.value, ubble_fraud_models.UbbleScore.UNDECIDABLE.value],
    )
    def test_decision_document_not_supported(self, client, ubble_mocker, ref_data_check_score):
        user, ubble_fraud_check, request_data = self._init_decision_test()

        ubble_identification_response = test_factories.UbbleIdentificationResponseFactory(
            identification_state=test_factories.IdentificationState.INVALID,  # 0
            data__attributes__identification_id=str(request_data.identification_id),
            included=[
                test_factories.UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=None,
                    attributes__document_number=None,
                    attributes__document_type=None,
                    attributes__first_name=None,
                    attributes__last_name=None,
                ),
                test_factories.UbbleIdentificationIncludedDocumentChecksFactory(
                    attributes__supported=ubble_fraud_models.UbbleScore.INVALID.value,  # 0
                    attributes__data_extracted_score=ubble_fraud_models.UbbleScore.UNDECIDABLE.value,  # -1
                    attributes__expiry_date_score=ubble_fraud_models.UbbleScore.UNDECIDABLE.value,  # -1
                    attributes__issue_date_score=ubble_fraud_models.UbbleScore.UNDECIDABLE.value,
                    attributes__live_video_capture_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__mrz_validity_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__mrz_viz_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_back_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_front_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__quality_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__visual_back_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__visual_front_score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedFaceChecksFactory(
                    attributes__active_liveness_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__live_video_capture_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__quality_score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedDocFaceMatchesFactory(
                    attributes__score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedReferenceDataChecksFactory(
                    attributes__score=ref_data_check_score,  # 1 or -1
                ),
            ],
        )

        self._post_webhook(client, ubble_mocker, request_data, ubble_identification_response)

        db.session.refresh(user)
        db.session.refresh(ubble_fraud_check)
        self._log_for_debug(user, ubble_fraud_check)

        assert not user.has_beneficiary_role
        assert ubble_fraud_check.status == fraud_models.FraudCheckStatus.SUSPICIOUS
        assert fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED in ubble_fraud_check.reasonCodes

        assert ubble_fraud_api.is_user_allowed_to_perform_ubble_check(user, user.eligibility)  # retry allowed

        message = subscription_models.SubscriptionMessage.query.one()
        assert (
            message.userMessage
            == "Ton document d'identité ne te permet pas de bénéficier du pass Culture. Réessaye avec un passeport ou une carte d'identité française en cours de validité."
        )
        assert message.callToActionLink == subscription_messages.REDIRECT_TO_IDENTIFICATION
        assert message.callToActionIcon == subscription_models.CallToActionIcon.RETRY
        assert message.callToActionTitle == "Réessayer la vérification de mon identité"

        self._assert_email_sent(user, 385)

    @pytest.mark.parametrize(
        "doc_supported", [ubble_fraud_models.UbbleScore.VALID.value, ubble_fraud_models.UbbleScore.UNDECIDABLE.value]
    )
    @pytest.mark.parametrize(
        "ref_data_check_score",
        [ubble_fraud_models.UbbleScore.VALID.value, ubble_fraud_models.UbbleScore.UNDECIDABLE.value],
    )
    def test_decision_document_expired(self, client, ubble_mocker, ref_data_check_score, doc_supported):
        user, ubble_fraud_check, request_data = self._init_decision_test()

        ubble_identification_response = test_factories.UbbleIdentificationResponseFactory(
            identification_state=test_factories.IdentificationState.INVALID,  # 0
            data__attributes__identification_id=str(request_data.identification_id),
            included=[
                test_factories.UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=None,
                    attributes__document_number=None,
                    attributes__document_type=None,
                    attributes__first_name=None,
                    attributes__last_name=None,
                ),
                test_factories.UbbleIdentificationIncludedDocumentChecksFactory(
                    attributes__supported=doc_supported,  # 1 or -1
                    attributes__data_extracted_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__expiry_date_score=ubble_fraud_models.UbbleScore.INVALID.value,  # 0
                    attributes__issue_date_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__live_video_capture_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__mrz_validity_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__mrz_viz_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_back_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_front_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__quality_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__visual_back_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__visual_front_score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedFaceChecksFactory(
                    attributes__active_liveness_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__live_video_capture_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__quality_score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedDocFaceMatchesFactory(
                    attributes__score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedReferenceDataChecksFactory(
                    attributes__score=ref_data_check_score,  # 1 or -1
                ),
            ],
        )

        self._post_webhook(client, ubble_mocker, request_data, ubble_identification_response)

        db.session.refresh(user)
        db.session.refresh(ubble_fraud_check)
        self._log_for_debug(user, ubble_fraud_check)

        assert not user.has_beneficiary_role
        assert ubble_fraud_check.status == fraud_models.FraudCheckStatus.SUSPICIOUS
        assert fraud_models.FraudReasonCode.ID_CHECK_EXPIRED in ubble_fraud_check.reasonCodes
        assert fraud_models.FraudReasonCode.MISSING_REQUIRED_DATA in ubble_fraud_check.reasonCodes

        assert ubble_fraud_api.is_user_allowed_to_perform_ubble_check(user, user.eligibility)  # retry allowed

        message = subscription_models.SubscriptionMessage.query.one()
        assert (
            message.userMessage
            == "Ton document d'identité est expiré. Réessaye avec un passeport ou une carte d'identité française en cours de validité."
        )
        assert message.callToActionLink == subscription_messages.REDIRECT_TO_IDENTIFICATION
        assert message.callToActionIcon == subscription_models.CallToActionIcon.RETRY
        assert message.callToActionTitle == "Réessayer la vérification de mon identité"

        self._assert_email_sent(user, 384)

    def test_decision_document_not_authentic(self, client, ubble_mocker):
        user, ubble_fraud_check, request_data = self._init_decision_test()

        ubble_identification_response = test_factories.UbbleIdentificationResponseFactory(
            identification_state=test_factories.IdentificationState.INVALID,
            data__attributes__identification_id=str(request_data.identification_id),
            included=[
                test_factories.UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=(
                        datetime.datetime.utcnow().date() - relativedelta.relativedelta(years=18, months=1)
                    ).isoformat(),
                    attributes__document_number="012345678910",
                    attributes__document_type="CI",
                    attributes__first_name="John",
                    attributes__last_name="Doe",
                ),
                test_factories.UbbleIdentificationIncludedDocumentChecksFactory(
                    attributes__supported=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__data_extracted_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__expiry_date_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__issue_date_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__live_video_capture_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__mrz_validity_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__mrz_viz_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_back_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_front_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_score=ubble_fraud_models.UbbleScore.INVALID.value,
                    attributes__quality_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__visual_back_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__visual_front_score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedFaceChecksFactory(
                    attributes__active_liveness_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__live_video_capture_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__quality_score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedDocFaceMatchesFactory(
                    attributes__score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedReferenceDataChecksFactory(
                    attributes__score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
            ],
        )

        self._post_webhook(client, ubble_mocker, request_data, ubble_identification_response)

        db.session.refresh(user)
        db.session.refresh(ubble_fraud_check)

        assert not user.has_beneficiary_role
        assert ubble_fraud_check.status == fraud_models.FraudCheckStatus.SUSPICIOUS
        assert fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC in ubble_fraud_check.reasonCodes

        assert ubble_fraud_api.is_user_allowed_to_perform_ubble_check(user, user.eligibility)

        message = subscription_models.SubscriptionMessage.query.one()
        assert (
            message.userMessage
            == "Le document que tu as présenté n’est pas accepté car il s’agit d’une photo ou d’une copie de l’original. Réessaye avec un document original en cours de validité."
        )
        assert message.callToActionLink == subscription_messages.REDIRECT_TO_IDENTIFICATION
        assert message.callToActionIcon == subscription_models.CallToActionIcon.RETRY
        assert message.callToActionTitle == "Réessayer la vérification de mon identité"

        assert len(mails_testing.outbox) == 0

    def test_decision_document_not_authentic_no_retry_left(self, client, ubble_mocker):
        user, ubble_fraud_check, request_data = self._init_decision_test()
        fraud_factories.BeneficiaryFraudCheckFactory.create_batch(
            2,
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC],
        )

        ubble_identification_response = test_factories.UbbleIdentificationResponseFactory(
            identification_state=test_factories.IdentificationState.INVALID,
            data__attributes__identification_id=str(request_data.identification_id),
            included=[
                test_factories.UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=(
                        datetime.datetime.utcnow().date() - relativedelta.relativedelta(years=18, months=1)
                    ).isoformat(),
                    attributes__document_number="012345678910",
                    attributes__document_type="CI",
                    attributes__first_name="John",
                    attributes__last_name="Doe",
                ),
                test_factories.UbbleIdentificationIncludedDocumentChecksFactory(
                    attributes__supported=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__data_extracted_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__expiry_date_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__issue_date_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__live_video_capture_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__mrz_validity_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__mrz_viz_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_back_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_front_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_score=ubble_fraud_models.UbbleScore.INVALID.value,
                    attributes__quality_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__visual_back_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__visual_front_score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedFaceChecksFactory(
                    attributes__active_liveness_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__live_video_capture_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__quality_score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedDocFaceMatchesFactory(
                    attributes__score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedReferenceDataChecksFactory(
                    attributes__score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
            ],
        )

        self._post_webhook(client, ubble_mocker, request_data, ubble_identification_response)

        db.session.refresh(user)
        db.session.refresh(ubble_fraud_check)

        assert not user.has_beneficiary_role
        assert ubble_fraud_check.status == fraud_models.FraudCheckStatus.SUSPICIOUS
        assert fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC in ubble_fraud_check.reasonCodes

        assert not ubble_fraud_api.is_user_allowed_to_perform_ubble_check(user, user.eligibility)

        message = subscription_models.SubscriptionMessage.query.one()
        assert (
            message.userMessage
            == "Ton dossier a été rejeté car le document que tu as présenté n’est pas authentique.  Passe par le site démarches simplifiées pour renouveler ta demande."
        )
        assert message.callToActionLink == subscription_messages.REDIRECT_TO_DMS_VIEW
        assert message.callToActionIcon == subscription_models.CallToActionIcon.EXTERNAL
        assert message.callToActionTitle == "Accéder au site Démarches-Simplifiées"

        assert len(mails_testing.outbox) == 0

    @pytest.mark.parametrize(
        "expiry_score", [ubble_fraud_models.UbbleScore.VALID.value, ubble_fraud_models.UbbleScore.UNDECIDABLE.value]
    )
    @pytest.mark.parametrize(
        "doc_supported", [ubble_fraud_models.UbbleScore.VALID.value, ubble_fraud_models.UbbleScore.UNDECIDABLE.value]
    )
    @pytest.mark.parametrize(
        "ref_data_check_score",
        [ubble_fraud_models.UbbleScore.VALID.value, ubble_fraud_models.UbbleScore.UNDECIDABLE.value],
    )
    def test_decision_invalid_for_another_reason(
        self, client, ubble_mocker, ref_data_check_score, doc_supported, expiry_score
    ):
        user, ubble_fraud_check, request_data = self._init_decision_test()

        ubble_identification_response = test_factories.UbbleIdentificationResponseFactory(
            identification_state=test_factories.IdentificationState.INVALID,  # 0
            data__attributes__identification_id=str(request_data.identification_id),
            included=[
                test_factories.UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=None,
                    attributes__document_number=None,
                    attributes__document_type=None,
                    attributes__first_name=None,
                    attributes__last_name=None,
                ),
                test_factories.UbbleIdentificationIncludedDocumentChecksFactory(
                    attributes__supported=doc_supported,  # 1 or -1
                    attributes__data_extracted_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__expiry_date_score=expiry_score,  # 1 or -1
                    attributes__issue_date_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__live_video_capture_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__mrz_validity_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__mrz_viz_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_back_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_front_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__quality_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__visual_back_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__visual_front_score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedFaceChecksFactory(
                    attributes__active_liveness_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__live_video_capture_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__quality_score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedDocFaceMatchesFactory(
                    attributes__score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedReferenceDataChecksFactory(
                    attributes__score=ref_data_check_score,  # 1 or -1
                ),
            ],
        )

        self._post_webhook(client, ubble_mocker, request_data, ubble_identification_response)

        db.session.refresh(user)
        db.session.refresh(ubble_fraud_check)
        self._log_for_debug(user, ubble_fraud_check)

        assert not user.has_beneficiary_role
        assert ubble_fraud_check.status == fraud_models.FraudCheckStatus.KO
        assert fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER in ubble_fraud_check.reasonCodes

        assert not ubble_fraud_api.is_user_allowed_to_perform_ubble_check(user, user.eligibility)  # retry not allowed

        message = subscription_models.SubscriptionMessage.query.one()
        assert (
            message.userMessage
            == "Ton dossier a été bloqué : Les informations que tu as renseignées ne te permettent pas de bénéficier du pass Culture."
        )
        assert message.popOverIcon == subscription_models.PopOverIcon.ERROR

        assert len(mails_testing.outbox) == 0

    @pytest.mark.parametrize(
        "expiry_score",
        [
            ubble_fraud_models.UbbleScore.VALID.value,
            ubble_fraud_models.UbbleScore.UNDECIDABLE.value,
            ubble_fraud_models.UbbleScore.UNDECIDABLE.value,
        ],
    )
    @pytest.mark.parametrize(
        "doc_supported",
        [
            ubble_fraud_models.UbbleScore.VALID.value,
            ubble_fraud_models.UbbleScore.UNDECIDABLE.value,
            ubble_fraud_models.UbbleScore.UNDECIDABLE.value,
        ],
    )
    @pytest.mark.parametrize(
        "ref_data_check_score",
        [
            ubble_fraud_models.UbbleScore.VALID.value,
            ubble_fraud_models.UbbleScore.UNDECIDABLE.value,
            ubble_fraud_models.UbbleScore.UNDECIDABLE.value,
        ],
    )
    def test_decision_unprocessable(self, client, ubble_mocker, ref_data_check_score, doc_supported, expiry_score):
        user, ubble_fraud_check, request_data = self._init_decision_test()

        ubble_identification_response = test_factories.UbbleIdentificationResponseFactory(
            identification_state=test_factories.IdentificationState.UNPROCESSABLE,  # -1
            data__attributes__identification_id=str(request_data.identification_id),
            included=[
                test_factories.UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=None,
                    attributes__document_number=None,
                    attributes__document_type=None,
                    attributes__first_name=None,
                    attributes__last_name=None,
                ),
                test_factories.UbbleIdentificationIncludedDocumentChecksFactory(
                    attributes__supported=doc_supported,  # 1, 0 or -1
                    attributes__data_extracted_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__expiry_date_score=expiry_score,  # 1, 0 or -1
                    attributes__issue_date_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__live_video_capture_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__mrz_validity_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__mrz_viz_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_back_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_front_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__ove_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__quality_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__visual_back_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__visual_front_score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedFaceChecksFactory(
                    attributes__active_liveness_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__live_video_capture_score=ubble_fraud_models.UbbleScore.VALID.value,
                    attributes__quality_score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedDocFaceMatchesFactory(
                    attributes__score=ubble_fraud_models.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedReferenceDataChecksFactory(
                    attributes__score=ref_data_check_score,  # 1, 0 or -1
                ),
            ],
        )

        self._post_webhook(client, ubble_mocker, request_data, ubble_identification_response)

        db.session.refresh(user)
        db.session.refresh(ubble_fraud_check)
        self._log_for_debug(user, ubble_fraud_check)

        assert not user.has_beneficiary_role
        assert ubble_fraud_check.status == fraud_models.FraudCheckStatus.SUSPICIOUS
        assert fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE in ubble_fraud_check.reasonCodes

        assert ubble_fraud_api.is_user_allowed_to_perform_ubble_check(user, user.eligibility)  # retry allowed

        message = subscription_models.SubscriptionMessage.query.one()
        assert (
            message.userMessage
            == "Nous n'avons pas réussi à lire ton document. Réessaye avec un passeport ou une carte d'identité française en cours de validité dans un lieu bien éclairé."
        )
        assert message.callToActionLink == subscription_messages.REDIRECT_TO_IDENTIFICATION
        assert message.callToActionIcon == subscription_models.CallToActionIcon.RETRY
        assert message.callToActionTitle == "Réessayer la vérification de mon identité"

        self._assert_email_sent(user, 304)
