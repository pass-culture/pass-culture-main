import datetime

from dateutil.relativedelta import relativedelta
import pytest

import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import models as users_models
import pcapi.core.users.factories as users_factories
from pcapi.utils.string import u_nbsp


@pytest.mark.usefixtures("db_session")
class BannerTest:
    # - authenticated user
    # - user joinloaded with subscription data
    expected_num_queries_without_subscription_check = 2
    # - 3 feature flags checked
    expected_num_queries_with_subscription_check = expected_num_queries_without_subscription_check + 3

    def setup_method(self):
        self.geolocation_banner = {
            "banner": {
                "name": "geolocation_banner",
                "title": "Géolocalise-toi",
                "text": "pour trouver des offres autour de toi",
            }
        }
        self.activation_banner = {
            "banner": {
                "name": "activation_banner",
                "title": f"Débloque tes 300{u_nbsp}€",
                "text": "à dépenser sur l'application",
            }
        }

    def should_not_be_allowed_to_get_banner_when_inactive(self, client):
        user = users_factories.UserFactory(isActive=False)

        client.with_token(email=user.email)
        response = client.get("/native/v1/banner")

        assert response.status_code == 403

    def should_be_allowed_to_get_banner_when_active(self, client):
        user = users_factories.UserFactory()

        client.with_token(email=user.email)
        with assert_num_queries(self.expected_num_queries_without_subscription_check):
            response = client.get("/native/v1/banner")
            assert response.status_code == 200

    def should_return_geolocation_banner_when_not_geolocated(self, client):
        user = users_factories.UserFactory()

        client.with_token(email=user.email)
        with assert_num_queries(self.expected_num_queries_without_subscription_check):
            response = client.get("/native/v1/banner?isGeolocated=false")
            assert response.status_code == 200

        assert response.json == self.geolocation_banner

    def should_return_activation_banner_when_user_has_phone_validation_to_complete(self, client):
        dateOfBirth = datetime.datetime.utcnow() - relativedelta(years=18, months=5)
        user = users_factories.UserFactory(dateOfBirth=dateOfBirth)

        client.with_token(email=user.email)
        with assert_num_queries(self.expected_num_queries_without_subscription_check + 1):  # 1 FF checked
            response = client.get("/native/v1/banner?isGeolocated=false")
            assert response.status_code == 200

        assert response.json == self.activation_banner

    def should_return_activation_banner_when_user_has_profile_to_complete(self, client):
        dateOfBirth = datetime.datetime.utcnow() - relativedelta(years=18, months=5)
        user = users_factories.UserFactory(
            dateOfBirth=dateOfBirth, phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )

        client.with_token(email=user.email)
        with assert_num_queries(self.expected_num_queries_without_subscription_check):
            response = client.get("/native/v1/banner?isGeolocated=false")
            assert response.status_code == 200

        assert response.json == self.activation_banner

    def should_return_activation_banner_when_user_has_identity_check_to_complete(self, client):
        dateOfBirth = datetime.datetime.utcnow() - relativedelta(years=18, months=5)
        user = users_factories.UserFactory(
            dateOfBirth=dateOfBirth, phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.PROFILE_COMPLETION, status=fraud_models.FraudCheckStatus.OK
        )

        client.with_token(email=user.email)
        with assert_num_queries(self.expected_num_queries_with_subscription_check):
            response = client.get("/native/v1/banner?isGeolocated=false")
            assert response.status_code == 200

        assert response.json == self.activation_banner

    def should_return_activation_banner_when_user_has_honor_statement_to_complete(self, client):
        dateOfBirth = datetime.datetime.utcnow() - relativedelta(years=18, months=5)
        user = users_factories.UserFactory(
            dateOfBirth=dateOfBirth, phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.PROFILE_COMPLETION, status=fraud_models.FraudCheckStatus.OK
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.OK
        )

        client.with_token(email=user.email)
        with assert_num_queries(self.expected_num_queries_with_subscription_check):
            response = client.get("/native/v1/banner?isGeolocated=false")
            assert response.status_code == 200

        assert response.json == self.activation_banner

    def should_not_return_any_banner_when_beneficiary_and_geolocated(self, client):
        user = users_factories.BeneficiaryGrant18Factory()

        client.with_token(email=user.email)
        with assert_num_queries(self.expected_num_queries_without_subscription_check):
            response = client.get("/native/v1/banner?isGeolocated=true")
            assert response.status_code == 200

        assert response.json == {"banner": None}

    def should_return_activation_banner_with_20_euros_when_15_year_old(self, client):
        dateOfBirth = datetime.datetime.utcnow() - relativedelta(years=15, months=5)
        user = users_factories.UserFactory(dateOfBirth=dateOfBirth)

        client.with_token(email=user.email)

        # authenticated user + joined user
        with assert_num_queries(2):
            response = client.get("/native/v1/banner?isGeolocated=false")
            assert response.status_code == 200

        assert response.json == {
            "banner": {
                "name": "activation_banner",
                "title": f"Débloque tes 20{u_nbsp}€",
                "text": "à dépenser sur l'application",
            }
        }

    def should_return_retry_banner_on_ubble_retry(self, client):
        user = users_factories.EligibleGrant18Factory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        fraud_factories.UbbleRetryFraudCheckFactory(user=user)

        client.with_token(email=user.email)
        with assert_num_queries(self.expected_num_queries_with_subscription_check):
            response = client.get("/native/v1/banner")
            assert response.status_code == 200

        assert response.json == {
            "banner": {
                "name": "retry_identity_check_banner",
                "title": "Nous n’avons pas pu vérifier ton identité",
                "text": "Réessaie dès maintenant",
            }
        }

    def should_get_15_18_transition_banner(self, client):
        user = users_factories.ExUnderageBeneficiaryFactory()

        client.with_token(email=user.email)
        with assert_num_queries(
            self.expected_num_queries_without_subscription_check + 1
        ):  # FF ENABLE_PHONE_VALIDATION checked
            response = client.get("/native/v1/banner")
            assert response.status_code == 200

        assert response.json == {
            "banner": {
                "name": "transition_17_18_banner",
                "text": "Confirme ton identité",
                "title": f"Débloque tes 300{u_nbsp}€",
            },
        }
