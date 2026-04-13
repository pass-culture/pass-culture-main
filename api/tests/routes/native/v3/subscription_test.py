import pytest
import time_machine
from flask_jwt_extended.utils import create_access_token

from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import models as subscription_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.utils.string import u_nbsp


pytestmark = pytest.mark.usefixtures("db_session")


class SubscriptionStepperTest:
    def test_subscription_stepper_without_authentication(self, client, app):
        with assert_num_queries(0):  # User is not fetched if no token is provided
            response = client.get("/native/v3/subscription/stepper")
            assert response.status_code == 401

    def test_subscription_stepper_user_not_found(self, client, app):
        users_factories.EmailValidatedUserFactory(email="this-email@example.com")

        token = create_access_token("other-email@example.com", additional_claims={"user_claims": {"user_id": 0}})
        client.auth_header = {
            "Authorization": f"Bearer {token}",
        }

        with assert_num_queries(1):  # user
            response = client.get("/native/v3/subscription/stepper")
            assert response.status_code == 403

        assert response.json["email"] == ["Utilisateur introuvable"]

    def test_subscription_stepper_user_not_active(self, client):
        user = users_factories.EmailValidatedUserFactory(isActive=False)

        client.with_token(user)
        with assert_num_queries(1):  # user
            response = client.get("/native/v3/subscription/stepper")
            assert response.status_code == 403

        assert response.json["email"] == ["Utilisateur introuvable"]

    def test_subscription_stepper_for_17yo_with_just_email_validated(self, client):
        user = users_factories.EmailValidatedUserFactory(age=17)

        client.with_token(user)
        # user
        # beneficiary_fraud_review
        # beneficiary_fraud_check
        # beneficiary_fraud_check
        with assert_num_queries(4):
            response = client.get("/native/v3/subscription/stepper")

        assert response.status_code == 200
        assert response.json == {
            "subscriptionStepsToDisplay": [
                {"name": "profile-completion", "title": "Profil", "subtitle": None, "completionState": "current"},
                {"name": "identity-check", "title": "Identification", "subtitle": None, "completionState": "disabled"},
                {"name": "honor-statement", "title": "Confirmation", "subtitle": None, "completionState": "disabled"},
            ],
            "allowedIdentityCheckMethods": ["educonnect", "ubble"],
            "hasIdentityCheckPending": False,
            "maintenancePageType": None,
            "nextSubscriptionStep": "profile-completion",
            "title": f"C'est très rapide{u_nbsp}!",
            "subtitle": f"Pour débloquer tes 50€ tu dois suivre les étapes suivantes{u_nbsp}:",
            "subscriptionMessage": None,
        }

    def test_subscription_stepper_for_18yo_with_just_email_validated(self, client):
        user = users_factories.EmailValidatedUserFactory(age=18)

        client.with_token(user)
        # user
        # beneficiary_fraud_review
        # beneficiary_fraud_check
        # beneficiary_fraud_check
        with assert_num_queries(4):
            response = client.get("/native/v3/subscription/stepper")

        assert response.status_code == 200
        assert response.json == {
            "subscriptionStepsToDisplay": [
                {"name": "profile-completion", "title": "Profil", "subtitle": None, "completionState": "current"},
                {"name": "identity-check", "title": "Identification", "subtitle": None, "completionState": "disabled"},
                {"name": "honor-statement", "title": "Confirmation", "subtitle": None, "completionState": "disabled"},
            ],
            "allowedIdentityCheckMethods": ["ubble"],
            "hasIdentityCheckPending": False,
            "maintenancePageType": None,
            "nextSubscriptionStep": "profile-completion",
            "title": f"C'est très rapide{u_nbsp}!",
            "subtitle": f"Pour débloquer tes 150€ tu dois suivre les étapes suivantes{u_nbsp}:",
            "subscriptionMessage": None,
        }

    def test_subscription_stepper_for_18yo_with_profile_completed(self, client):
        user = users_factories.ProfileCompletedUserFactory(age=18)

        client.with_token(user)
        # user
        # beneficiary_fraud_review
        # beneficiary_fraud_check
        # action_history
        # beneficiary_fraud_check
        with assert_num_queries(5):
            response = client.get("/native/v3/subscription/stepper")

        assert response.status_code == 200
        assert response.json == {
            "subscriptionStepsToDisplay": [
                {"name": "profile-completion", "title": "Profil", "subtitle": None, "completionState": "completed"},
                {"name": "identity-check", "title": "Identification", "subtitle": None, "completionState": "current"},
                {"name": "honor-statement", "title": "Confirmation", "subtitle": None, "completionState": "disabled"},
            ],
            "allowedIdentityCheckMethods": ["ubble"],
            "hasIdentityCheckPending": False,
            "maintenancePageType": None,
            "nextSubscriptionStep": "identity-check",
            "title": f"C'est très rapide{u_nbsp}!",
            "subtitle": f"Pour débloquer tes 150€ tu dois suivre les étapes suivantes{u_nbsp}:",
            "subscriptionMessage": None,
        }

    def test_subscription_stepper_for_18yo_with_identity_check_pending(self, client):
        user = users_factories.ProfileCompletedUserFactory(age=18)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            status=subscription_models.FraudCheckStatus.PENDING,
            type=subscription_models.FraudCheckType.UBBLE,
        )

        client.with_token(user)
        # user
        # beneficiary_fraud_review
        # beneficiary_fraud_check
        # action_history
        # beneficiary_fraud_check
        with assert_num_queries(5):
            response = client.get("/native/v3/subscription/stepper")

        assert response.status_code == 200
        assert response.json == {
            "subscriptionStepsToDisplay": [
                {"name": "profile-completion", "title": "Profil", "subtitle": None, "completionState": "completed"},
                {"name": "identity-check", "title": "Identification", "subtitle": None, "completionState": "completed"},
                {"name": "honor-statement", "title": "Confirmation", "subtitle": None, "completionState": "current"},
            ],
            "allowedIdentityCheckMethods": ["ubble"],
            "hasIdentityCheckPending": True,
            "maintenancePageType": None,
            "nextSubscriptionStep": "honor-statement",
            "title": f"C'est très rapide{u_nbsp}!",
            "subtitle": f"Pour débloquer tes 150€ tu dois suivre les étapes suivantes{u_nbsp}:",
            "subscriptionMessage": None,
        }

    @time_machine.travel("2026-03-27", tick=False)
    def test_subscription_stepper_for_18yo_with_dms_issue(self, client):
        user = users_factories.ProfileCompletedUserFactory(age=18)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            status=subscription_models.FraudCheckStatus.KO,
            type=subscription_models.FraudCheckType.DMS,
        )

        client.with_token(user)
        # user
        # beneficiary_fraud_review
        # beneficiary_fraud_check
        # action_history
        # beneficiary_fraud_check
        with assert_num_queries(5):
            response = client.get("/native/v3/subscription/stepper")

        assert response.status_code == 200
        assert response.json == {
            "subscriptionStepsToDisplay": [
                {"name": "profile-completion", "title": "Profil", "subtitle": None, "completionState": "completed"},
                {"name": "identity-check", "title": "Identification", "subtitle": None, "completionState": "completed"},
                {"name": "honor-statement", "title": "Confirmation", "subtitle": None, "completionState": "completed"},
            ],
            "allowedIdentityCheckMethods": ["ubble"],
            "hasIdentityCheckPending": False,
            "maintenancePageType": None,
            "nextSubscriptionStep": None,
            "title": "La vérification de ton identité a échoué",
            "subtitle": None,
            "subscriptionMessage": {
                "callToAction": None,
                "messageSummary": None,
                "popOverIcon": "ERROR",
                "updatedAt": "2026-03-27T00:00:00Z",
                "userMessage": "Ton dossier déposé sur le site demarche.numerique.gouv.fr a été refusé.",
            },
        }

    @time_machine.travel("2026-03-27", tick=False)
    def test_subscription_stepper_for_17yo_with_educonnect_issue(self, client):
        user = users_factories.ProfileCompletedUserFactory(age=17)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            status=subscription_models.FraudCheckStatus.KO,
            type=subscription_models.FraudCheckType.EDUCONNECT,
        )

        client.with_token(user)
        # user
        # beneficiary_fraud_review
        # beneficiary_fraud_check
        # action_history
        # beneficiary_fraud_check
        with assert_num_queries(5):
            response = client.get("/native/v3/subscription/stepper")

        assert response.status_code == 200
        assert response.json == {
            "subscriptionStepsToDisplay": [
                {"name": "profile-completion", "title": "Profil", "subtitle": None, "completionState": "completed"},
                {"name": "identity-check", "title": "Identification", "subtitle": None, "completionState": "retry"},
                {"name": "honor-statement", "title": "Confirmation", "subtitle": None, "completionState": "disabled"},
            ],
            "allowedIdentityCheckMethods": ["educonnect", "ubble"],
            "hasIdentityCheckPending": False,
            "maintenancePageType": None,
            "nextSubscriptionStep": "identity-check",
            "title": "La vérification de ton identité a échoué",
            "subtitle": None,
            "subscriptionMessage": {
                "callToAction": {
                    "callToActionIcon": "RETRY",
                    "callToActionLink": "https://webapp-v2.example.com/verification-identite",
                    "callToActionTitle": "Réessayer la vérification de mon identité",
                },
                "messageSummary": None,
                "popOverIcon": None,
                "updatedAt": "2026-03-27T00:00:00Z",
                "userMessage": "La vérification de ton identité a échoué. Tu peux réessayer.",
            },
        }

    @time_machine.travel("2026-03-27", tick=False)
    def test_subscription_stepper_for_18yo_with_ubble_issue(self, client):
        user = users_factories.ProfileCompletedUserFactory(age=18)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            status=subscription_models.FraudCheckStatus.KO,
            type=subscription_models.FraudCheckType.UBBLE,
            reasonCodes=[subscription_models.FraudReasonCode.ID_CHECK_EXPIRED],
        )

        client.with_token(user)
        # user
        # beneficiary_fraud_review
        # beneficiary_fraud_check
        # action_history
        # beneficiary_fraud_check
        with assert_num_queries(5):
            response = client.get("/native/v3/subscription/stepper")

        assert response.status_code == 200
        assert response.json == {
            "subscriptionStepsToDisplay": [
                {"name": "profile-completion", "title": "Profil", "subtitle": None, "completionState": "completed"},
                {
                    "name": "identity-check",
                    "title": "Identification",
                    "subtitle": "Réessaie avec un autre document d’identité valide",
                    "completionState": "retry",
                },
                {"name": "honor-statement", "title": "Confirmation", "subtitle": None, "completionState": "disabled"},
            ],
            "allowedIdentityCheckMethods": ["ubble"],
            "hasIdentityCheckPending": False,
            "maintenancePageType": None,
            "nextSubscriptionStep": "identity-check",
            "title": "La vérification de ton identité a échoué",
            "subtitle": None,
            "subscriptionMessage": {
                "callToAction": {
                    "callToActionIcon": "RETRY",
                    "callToActionLink": "https://webapp-v2.example.com/verification-identite",
                    "callToActionTitle": "Réessayer la vérification de mon identité",
                },
                "messageSummary": "Le document que tu as présenté est expiré.",
                "popOverIcon": None,
                "updatedAt": "2026-03-27T00:00:00Z",
                "userMessage": "Ton document d'identité est expiré. Réessaie avec un passeport ou une carte d'identité française en cours de validité.",
            },
        }

    def test_subscription_stepper_for_18yo_with_identity_check_completed(self, client):
        user = users_factories.IdentityValidatedUserFactory(age=18)

        client.with_token(user)
        # user
        # beneficiary_fraud_review
        # beneficiary_fraud_check
        # action_history
        # beneficiary_fraud_check
        with assert_num_queries(5):
            response = client.get("/native/v3/subscription/stepper")

        assert response.status_code == 200
        assert response.json == {
            "subscriptionStepsToDisplay": [
                {"name": "profile-completion", "title": "Profil", "subtitle": None, "completionState": "completed"},
                {"name": "identity-check", "title": "Identification", "subtitle": None, "completionState": "completed"},
                {"name": "honor-statement", "title": "Confirmation", "subtitle": None, "completionState": "current"},
            ],
            "allowedIdentityCheckMethods": ["ubble"],
            "hasIdentityCheckPending": False,
            "maintenancePageType": None,
            "nextSubscriptionStep": "honor-statement",
            "title": f"C'est très rapide{u_nbsp}!",
            "subtitle": f"Pour débloquer tes 150€ tu dois suivre les étapes suivantes{u_nbsp}:",
            "subscriptionMessage": None,
        }

    def test_subscription_stepper_for_18yo_with_honor_statement_completed(self, client):
        user = users_factories.HonorStatementValidatedUserFactory(age=18)

        client.with_token(user)
        # user
        # beneficiary_fraud_review
        # beneficiary_fraud_check
        # action_history
        # beneficiary_fraud_check
        with assert_num_queries(5):
            response = client.get("/native/v3/subscription/stepper")

        assert response.status_code == 200
        assert response.json == {
            "subscriptionStepsToDisplay": [
                {"name": "profile-completion", "title": "Profil", "subtitle": None, "completionState": "completed"},
                {"name": "identity-check", "title": "Identification", "subtitle": None, "completionState": "completed"},
                {"name": "honor-statement", "title": "Confirmation", "subtitle": None, "completionState": "completed"},
            ],
            "allowedIdentityCheckMethods": ["ubble"],
            "hasIdentityCheckPending": False,
            "maintenancePageType": None,
            "nextSubscriptionStep": None,
            "title": f"C'est très rapide{u_nbsp}!",
            "subtitle": f"Pour débloquer tes 150€ tu dois suivre les étapes suivantes{u_nbsp}:",
            "subscriptionMessage": None,
        }

    def test_subscription_stepper_for_transition1718_beneficiary(self, client):
        user = users_factories.Transition1718Factory()

        client.with_token(user)
        # user
        # deposit
        # beneficiary_fraud_review
        # beneficiary_fraud_check
        # action_history
        # beneficiary_fraud_check
        with assert_num_queries(6):
            response = client.get("/native/v3/subscription/stepper")

        assert response.status_code == 200
        assert response.json == {
            "subscriptionStepsToDisplay": [
                {
                    "name": "profile-completion",
                    "title": "Profil",
                    "subtitle": "Confirme tes informations",
                    "completionState": "current",
                },
                {"name": "honor-statement", "title": "Confirmation", "subtitle": None, "completionState": "disabled"},
            ],
            "allowedIdentityCheckMethods": ["ubble"],
            "hasIdentityCheckPending": False,
            "maintenancePageType": None,
            "nextSubscriptionStep": "profile-completion",
            "title": f"C'est très rapide{u_nbsp}!",
            "subtitle": f"Pour débloquer tes 150€ tu dois suivre les étapes suivantes{u_nbsp}:",
            "subscriptionMessage": None,
        }

    def test_subscription_stepper_for_18yo_beneficiary(self, client):
        user = users_factories.BeneficiaryFactory()

        client.with_token(user)
        # user
        # deposit
        # beneficiary_fraud_check
        # action_history
        # beneficiary_fraud_check
        with assert_num_queries(5):
            response = client.get("/native/v3/subscription/stepper")

        assert response.status_code == 200
        assert response.json == {
            "subscriptionStepsToDisplay": [
                {"name": "profile-completion", "title": "Profil", "subtitle": None, "completionState": "completed"},
                {"name": "identity-check", "title": "Identification", "subtitle": None, "completionState": "completed"},
                {"name": "honor-statement", "title": "Confirmation", "subtitle": None, "completionState": "completed"},
            ],
            "allowedIdentityCheckMethods": ["ubble"],
            "hasIdentityCheckPending": False,
            "maintenancePageType": None,
            "nextSubscriptionStep": None,
            "title": f"C'est très rapide{u_nbsp}!",
            "subtitle": f"Pour débloquer tes 150€ tu dois suivre les étapes suivantes{u_nbsp}:",
            "subscriptionMessage": None,
        }
