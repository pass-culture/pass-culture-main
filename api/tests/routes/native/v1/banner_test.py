import pytest
import time_machine
from dateutil.relativedelta import relativedelta

import pcapi.core.subscription.factories as subscription_factories
import pcapi.core.subscription.models as subscription_models
import pcapi.core.users.factories as users_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import models as users_models
from pcapi.utils import date as date_utils
from pcapi.utils.string import u_nbsp


@pytest.mark.usefixtures("db_session")
class BannerTest:
    # - authenticated user
    # - user
    # - beneficiary fraud checks
    # - beneficiary fraud reviews
    # - deposits
    expected_num_queries_without_subscription_check = 5
    # - all feature flags checked
    expected_num_queries_with_subscription_check = expected_num_queries_without_subscription_check + 1

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
                "title": f"Débloque tes 150{u_nbsp}€",
                "text": "à dépenser sur l'application",
            }
        }

    def should_not_be_allowed_to_get_banner_when_inactive(self, client):
        user = users_factories.UserFactory(isActive=False)

        expected_num_queries = 1  # user (authentication)

        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/banner")
            assert response.status_code == 403

    def should_be_allowed_to_get_banner_when_active(self, client):
        user = users_factories.UserFactory()

        client.with_token(user)
        with assert_num_queries(self.expected_num_queries_without_subscription_check):
            response = client.get("/native/v1/banner")
            assert response.status_code == 200

    def should_return_geolocation_banner_when_not_geolocated(self, client):
        user = users_factories.UserFactory()

        client.with_token(user)
        with assert_num_queries(self.expected_num_queries_without_subscription_check):
            response = client.get("/native/v1/banner?isGeolocated=false")
            assert response.status_code == 200

        assert response.json == self.geolocation_banner

    def should_return_activation_banner_when_user_has_phone_validation_to_complete(self, client):
        dateOfBirth = date_utils.get_naive_utc_now() - relativedelta(years=18, months=5)
        user = users_factories.UserFactory(dateOfBirth=dateOfBirth)

        client.with_token(user)
        with assert_num_queries(self.expected_num_queries_without_subscription_check):
            response = client.get("/native/v1/banner?isGeolocated=false")
            assert response.status_code == 200

        assert response.json == self.activation_banner

    def should_return_activation_banner_when_user_has_profile_to_complete(self, client):
        dateOfBirth = date_utils.get_naive_utc_now() - relativedelta(years=18, months=5)
        user = users_factories.UserFactory(
            dateOfBirth=dateOfBirth, phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )

        client.with_token(user)
        with assert_num_queries(self.expected_num_queries_without_subscription_check):
            response = client.get("/native/v1/banner?isGeolocated=false")
            assert response.status_code == 200

        assert response.json == self.activation_banner

    def should_return_activation_banner_when_user_has_identity_check_to_complete(self, client):
        dateOfBirth = date_utils.get_naive_utc_now() - relativedelta(years=18, months=5)
        user = users_factories.UserFactory(
            dateOfBirth=dateOfBirth, phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
        )

        client.with_token(user)
        expected_num_queries = self.expected_num_queries_without_subscription_check + 1  # action_history
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/banner?isGeolocated=false")
            assert response.status_code == 200

        assert response.json == self.activation_banner

    def should_return_activation_banner_when_user_has_honor_statement_to_complete(self, client):
        dateOfBirth = date_utils.get_naive_utc_now() - relativedelta(years=18, months=5)
        user = users_factories.UserFactory(
            dateOfBirth=dateOfBirth, phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user, type=subscription_models.FraudCheckType.UBBLE, status=subscription_models.FraudCheckStatus.OK
        )

        client.with_token(user)
        with assert_num_queries(self.expected_num_queries_with_subscription_check + 1):  # action_history
            response = client.get("/native/v1/banner?isGeolocated=false")
            assert response.status_code == 200

        assert response.json == self.activation_banner

    def should_not_return_any_banner_when_beneficiary_and_geolocated(self, client):
        user = users_factories.BeneficiaryGrant18Factory()

        client.with_token(user)
        with assert_num_queries(self.expected_num_queries_without_subscription_check):
            response = client.get("/native/v1/banner?isGeolocated=true")
            assert response.status_code == 200

        assert response.json == {"banner": None}

    def should_return_activation_banner_with_30_euros_when_17_year_old(self, client):
        user = users_factories.UserFactory(age=17)

        client.with_token(user)
        with assert_num_queries(self.expected_num_queries_without_subscription_check):
            response = client.get("/native/v1/banner?isGeolocated=false")
            assert response.status_code == 200

        assert response.json == {
            "banner": {
                "name": "activation_banner",
                "title": f"Débloque tes 50{u_nbsp}€",
                "text": "à dépenser sur l'application",
            }
        }

    def should_return_retry_banner_on_ubble_retry(self, client):
        user = users_factories.EligibleGrant18Factory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)
        subscription_factories.UbbleRetryFraudCheckFactory(user=user)

        client.with_token(user)
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

    def should_get_17_18_transition_id_check_todo_banner(self, client):
        user = users_factories.ExUnderageBeneficiaryFactory()

        client.with_token(user)
        with assert_num_queries(self.expected_num_queries_without_subscription_check):
            response = client.get("/native/v1/banner")
            assert response.status_code == 200

        assert response.json == {
            "banner": {
                "name": "transition_17_18_banner",
                "text": "Vérifie ton identité",
                "title": f"Débloque tes 150{u_nbsp}€",
            },
        }

    def should_get_17_18_transition_id_check_done_banner(self, client):
        a_year_ago = date_utils.get_naive_utc_now() - relativedelta(years=1, months=1)
        with time_machine.travel(a_year_ago):
            user = users_factories.BeneficiaryFactory(age=17)

        assert user.age == 18

        client.with_token(user)
        with assert_num_queries(self.expected_num_queries_without_subscription_check):
            response = client.get("/native/v1/banner")
            assert response.status_code == 200

        assert response.json == {
            "banner": {
                "name": "transition_17_18_banner",
                "text": "Confirme tes informations",
                "title": f"Débloque tes 150{u_nbsp}€",
            },
        }

    def should_not_return_any_banner_for_free_eligibility(self, client):
        user = users_factories.EmailValidatedUserFactory(age=16)

        client.with_token(user)
        with assert_num_queries(self.expected_num_queries_without_subscription_check):
            response = client.get("/native/v1/banner?isGeolocated=true")

        assert response.status_code == 200
        assert response.json == {"banner": None}
