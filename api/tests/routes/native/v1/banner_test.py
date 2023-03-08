import datetime

from dateutil.relativedelta import relativedelta
import pytest

import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
from pcapi.core.users import models as users_models
import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
class BannerTest:
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
                "title": "Débloque tes 300 €",
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
        response = client.get("/native/v1/banner")

        assert response.status_code == 200

    def should_return_geolocation_banner_when_not_geolocated(self, client):
        user = users_factories.UserFactory()

        client.with_token(email=user.email)
        response = client.get("/native/v1/banner?isGeolocated=false")

        assert response.status_code == 200
        assert response.json == self.geolocation_banner

    def should_return_activation_banner_when_user_has_phone_validation_to_complete(self, client):
        dateOfBirth = datetime.datetime.utcnow() - relativedelta(years=18, months=5)
        user = users_factories.UserFactory(dateOfBirth=dateOfBirth)

        client.with_token(email=user.email)
        response = client.get("/native/v1/banner?isGeolocated=false")

        assert response.status_code == 200
        assert response.json == self.activation_banner

    def should_return_activation_banner_when_user_has_profile_to_complete(self, client):
        dateOfBirth = datetime.datetime.utcnow() - relativedelta(years=18, months=5)
        user = users_factories.UserFactory(
            dateOfBirth=dateOfBirth, phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )

        client.with_token(email=user.email)
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
        response = client.get("/native/v1/banner?isGeolocated=false")

        assert response.status_code == 200
        assert response.json == self.activation_banner

    def should_not_return_any_banner_when_beneficiary_and_geolocated(self, client):
        user = users_factories.BeneficiaryGrant18Factory()

        client.with_token(email=user.email)
        response = client.get("/native/v1/banner?isGeolocated=true")

        assert response.status_code == 200
        assert response.json == {"banner": None}

    def should_return_activation_banner_with_20_euros_when_15_year_old(self, client):
        dateOfBirth = datetime.datetime.utcnow() - relativedelta(years=15, months=5)
        user = users_factories.UserFactory(dateOfBirth=dateOfBirth)

        client.with_token(email=user.email)
        response = client.get("/native/v1/banner?isGeolocated=false")

        assert response.status_code == 200
        assert response.json == {
            "banner": {
                "name": "activation_banner",
                "title": "Débloque tes 20 €",
                "text": "à dépenser sur l'application",
            }
        }
