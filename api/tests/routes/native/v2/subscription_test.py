import pytest
from flask_jwt_extended.utils import create_access_token

from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.utils.string import u_nbsp


pytestmark = pytest.mark.usefixtures("db_session")


class SubscriptionStepperTest:
    def test_subscription_stepper_without_authentication(self, client, app):
        with assert_num_queries(0):  # User is not fetched if no token is provided
            response = client.get("/native/v2/subscription/stepper")
            assert response.status_code == 401

    def test_subscription_stepper_user_not_found(self, client, app):
        users_factories.EmailValidatedUserFactory(email="this-email@example.com")

        token = create_access_token("other-email@example.com", additional_claims={"user_claims": {"user_id": 0}})
        client.auth_header = {
            "Authorization": f"Bearer {token}",
        }

        with assert_num_queries(1):  # user
            response = client.get("/native/v2/subscription/stepper")
            assert response.status_code == 403

        assert response.json["email"] == ["Utilisateur introuvable"]

    def test_subscription_stepper_user_not_active(self, client):
        user = users_factories.EmailValidatedUserFactory(isActive=False)

        client.with_token(user)
        with assert_num_queries(1):  # user
            response = client.get("/native/v2/subscription/stepper")
            assert response.status_code == 403

        assert response.json["email"] == ["Utilisateur introuvable"]

    def test_subscription_stepper_for_free_16yo_with_just_email_validated(self, client):
        user = users_factories.EmailValidatedUserFactory(age=16)

        client.with_token(user)
        # user
        # beneficiary_fraud_check
        # beneficiary_fraud_review
        # beneficiary_fraud_check
        with assert_num_queries(4):
            response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json == {
            "subscriptionStepsToDisplay": [
                {"name": "profile-completion", "title": "Profil", "subtitle": None, "completionState": "current"},
                {"name": "honor-statement", "title": "Confirmation", "subtitle": None, "completionState": "disabled"},
            ],
            "allowedIdentityCheckMethods": ["ubble"],
            "hasIdentityCheckPending": False,
            "maintenancePageType": None,
            "nextSubscriptionStep": "profile-completion",
            "title": f"C'est très rapide{u_nbsp}!",
            "subtitle": f"Pour débloquer tes 30€ tu dois suivre les étapes suivantes{u_nbsp}:",
            "subscriptionMessage": None,
        }

    def test_subscription_stepper_for_17yo_with_just_email_validated(self, client):
        user = users_factories.EmailValidatedUserFactory(age=17)

        client.with_token(user)
        # user
        # beneficiary_fraud_review
        # beneficiary_fraud_check
        # beneficiary_fraud_check
        with assert_num_queries(4):
            response = client.get("/native/v2/subscription/stepper")

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
            response = client.get("/native/v2/subscription/stepper")

        assert response.status_code == 200
        assert response.json == {
            "subscriptionStepsToDisplay": [
                {
                    "name": "phone-validation",
                    "title": "Numéro de téléphone",
                    "subtitle": None,
                    "completionState": "current",
                },
                {"name": "profile-completion", "title": "Profil", "subtitle": None, "completionState": "disabled"},
                {"name": "identity-check", "title": "Identification", "subtitle": None, "completionState": "disabled"},
                {"name": "honor-statement", "title": "Confirmation", "subtitle": None, "completionState": "disabled"},
            ],
            "allowedIdentityCheckMethods": ["ubble"],
            "hasIdentityCheckPending": False,
            "maintenancePageType": None,
            "nextSubscriptionStep": "phone-validation",
            "title": f"C'est très rapide{u_nbsp}!",
            "subtitle": f"Pour débloquer tes 150€ tu dois suivre les étapes suivantes{u_nbsp}:",
            "subscriptionMessage": None,
        }
