import dataclasses
from datetime import date
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
import logging
from unittest import mock
from unittest.mock import patch
from urllib.parse import parse_qs
from urllib.parse import urlparse

from dateutil.relativedelta import relativedelta
import fakeredis
import jwt
import pytest
import time_machine

from pcapi import settings
from pcapi.connectors.google_oauth import GoogleUser
from pcapi.core import testing
from pcapi.core import token as token_utils
from pcapi.core.bookings import factories as booking_factories
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.factories import CancelledBookingFactory
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.models as finance_models
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.ubble import models as ubble_fraud_models
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.subscription.api as subscription_api
import pcapi.core.subscription.models as subscription_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users import testing as users_testing
from pcapi.core.users import young_status
from pcapi.core.users.api import create_phone_validation_token
import pcapi.core.users.constants as users_constants
from pcapi.core.users.email import request_email_update_with_credentials
from pcapi.core.users.email import update as email_update
from pcapi.core.users.email.repository import get_email_update_latest_event
from pcapi.core.users.utils import ALGORITHM_HS_256
from pcapi.core.users.utils import encode_jwt_payload
from pcapi.models import db
from pcapi.notifications.push import testing as push_testing
from pcapi.notifications.sms import testing as sms_testing
from pcapi.routes.native.v1.api_errors import account as account_errors
from pcapi.routes.native.v1.serialization import account as account_serializers


pytestmark = pytest.mark.usefixtures("db_session")


class AccountTest:
    identifier = "email@example.com"

    def test_get_user_profile_without_authentication(self, client, app):
        users_factories.UserFactory(email=self.identifier)

        response = client.get("/native/v1/me")

        assert response.status_code == 401

    def test_get_user_profile_not_found(self, client, app):
        users_factories.UserFactory(email=self.identifier)

        client.with_token(email="other-email@example.com")
        with assert_num_queries(1):  # user
            response = client.get("/native/v1/me")
            assert response.status_code == 403

        assert response.json["email"] == ["Utilisateur introuvable"]

    def test_get_user_profile_not_active(self, client, app):
        users_factories.UserFactory(email=self.identifier, isActive=False)

        client.with_token(email=self.identifier)
        with assert_num_queries(1):  # user
            response = client.get("/native/v1/me")
            assert response.status_code == 403

        assert response.json["email"] == ["Utilisateur introuvable"]

    @time_machine.travel("2018-06-01", tick=False)
    @override_features(ENABLE_NATIVE_CULTURAL_SURVEY=True)
    def test_get_user_profile(self, client, app):
        USER_DATA = {
            "email": self.identifier,
            "firstName": "john",
            "lastName": "doe",
            "phoneNumber": "+33102030405",
            "needsToFillCulturalSurvey": True,
        }
        user = users_factories.BeneficiaryGrant18Factory(
            dateOfBirth=datetime(2000, 1, 1),
            # The expiration date is taken in account in
            # `get_wallet_balance` and compared against the SQL
            # `now()` function, which is NOT overridden by
            # `time_machine.travel()`.
            deposit__expirationDate=datetime(2040, 1, 1),
            notificationSubscriptions={"marketing_push": True},
            validatedBirthDate=datetime(2000, 1, 11),
            **USER_DATA,
        )
        users_factories.DepositGrantFactory(
            user=user, type=finance_models.DepositType.GRANT_15_17, dateCreated=datetime(2015, 2, 3)
        )

        booking = BookingFactory(user=user, amount=Decimal("123.45"))
        CancelledBookingFactory(user=user, amount=Decimal("123.45"))

        expected_num_queries = (
            5  # user + deposit + booking(from _get_booked_offers) + booking (from get_domains_credit) + feature
        )
        client.with_token(self.identifier)
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/me")
            assert response.status_code == 200

        EXPECTED_DATA = {
            "id": user.id,
            "bookedOffers": {str(booking.stock.offer.id): booking.id},
            "domainsCredit": {
                "all": {"initial": 30000, "remaining": 17655},
                "digital": {"initial": 10000, "remaining": 10000},
                "physical": None,
            },
            "birthDate": "2000-01-11",
            "depositType": "GRANT_18",
            "depositActivationDate": "2018-06-01T00:00:00Z",
            "firstDepositActivationDate": "2015-02-03T00:00:00Z",
            "depositExpirationDate": "2040-01-01T00:00:00Z",
            "eligibility": "age-18",
            "eligibilityEndDatetime": "2019-01-11T11:00:00Z",
            "eligibilityStartDatetime": "2015-01-11T00:00:00Z",
            "hasPassword": True,
            "isBeneficiary": True,
            "isEligibleForBeneficiaryUpgrade": False,
            "roles": ["BENEFICIARY"],
            "recreditAmountToShow": None,
            "requiresIdCheck": True,
            "showEligibleCard": False,
            "subscriptions": {"marketingPush": True, "marketingEmail": True, "subscribedThemes": []},
            "subscriptionMessage": None,
            "status": {
                "statusType": young_status.YoungStatusType.BENEFICIARY.value,
                "subscriptionStatus": None,
            },
        }
        EXPECTED_DATA.update(USER_DATA)

        assert response.json == EXPECTED_DATA

    def test_status_contains_subscription_status_when_eligible(self, client):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18))

        expected_num_queries = (
            6  # user + beneficiary_fraud_review + feature + beneficiary_fraud_check + deposit + booking
        )

        client.with_token(user.email)
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/me")

        assert response.json["status"] == {
            "statusType": young_status.YoungStatusType.ELIGIBLE.value,
            "subscriptionStatus": young_status.SubscriptionStatus.HAS_TO_COMPLETE_SUBSCRIPTION.value,
        }

    def test_get_user_not_beneficiary(self, client, app):
        users_factories.UserFactory(email=self.identifier)

        expected_num_queries = 4  # user + beneficiary_fraud_review + deposit + booking

        client.with_token(email=self.identifier)

        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/me")
            assert response.status_code == 200

        assert not response.json["domainsCredit"]

    def test_get_user_profile_empty_first_name(self, client, app):
        users_factories.UserFactory(email=self.identifier, firstName="")

        expected_num_queries = 4  # user + beneficiary_fraud_review + deposit + booking

        client.with_token(email=self.identifier)
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/me")
            assert response.status_code == 200

        assert response.json["email"] == self.identifier
        assert response.json["firstName"] is None
        assert not response.json["isBeneficiary"]
        assert response.json["roles"] == []

    def test_get_user_profile_recredit_amount_to_show(self, client, app):
        with time_machine.travel("2020-01-01"):
            users_factories.UnderageBeneficiaryFactory(email=self.identifier)

        with time_machine.travel("2021-01-02"):
            finance_api.recredit_underage_users()

        client.with_token(email=self.identifier)
        me_response = client.get("/native/v1/me")
        assert me_response.json["recreditAmountToShow"] == 3000

    @override_features(ENABLE_UBBLE=False)
    def test_maintenance_message(self, client):
        """
        Test that when a user has no subscription message and when the
        whole beneficiary signup process has been deactivated, the call
        to /me returns a generic maintenance message.
        """
        user = users_factories.UserFactory(
            activity=users_models.ActivityEnum.STUDENT.value,
            dateOfBirth=datetime.utcnow() - relativedelta(years=18, days=5),
            email=self.identifier,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        client.with_token(user.email)

        expected_num_queries = (
            6  # user + beneficiary_fraud_review + beneficiary_fraud_check + feature + deposit + booking
        )
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/me")
        assert response.status_code == 200

        msg = response.json["subscriptionMessage"]
        assert (
            msg["userMessage"]
            == "La vérification d'identité est momentanément indisponible. L'équipe du pass Culture met tout en oeuvre pour la rétablir au plus vite."
        )
        assert msg["callToAction"] is None
        assert msg["popOverIcon"] == subscription_models.PopOverIcon.CLOCK.value

    def test_subscription_message_with_call_to_action(self, client):
        user = users_factories.UserFactory(
            activity=users_models.ActivityEnum.STUDENT.value,
            dateOfBirth=datetime.utcnow() - relativedelta(years=18, days=5),
            email=self.identifier,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED],
        )

        client.with_token(user.email)
        expected_num_queries = (
            6  # user + beneficiary_fraud_review + beneficiary_fraud_check + feature + deposit + booking
        )
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/me")
            assert response.status_code == 200

        msg = response.json["subscriptionMessage"]
        assert (
            msg["userMessage"]
            == "Le document d'identité que tu as présenté n'est pas accepté. S’il s’agit d’une pièce d’identité étrangère ou d’un titre de séjour français, tu dois passer par le site demarches-simplifiees.fr. Si non, tu peux réessayer avec un passeport ou une carte d’identité française en cours de validité."
        )
        assert msg["callToAction"] == {
            "callToActionIcon": "RETRY",
            "callToActionLink": "passculture://verification-identite",
            "callToActionTitle": "Réessayer la vérification de mon identité",
        }
        assert msg["popOverIcon"] is None

    @pytest.mark.parametrize(
        "feature_flags,roles,needsToFillCulturalSurvey",
        [
            (
                {"ENABLE_CULTURAL_SURVEY": True, "ENABLE_NATIVE_CULTURAL_SURVEY": True},
                [],
                False,
            ),
            (
                {"ENABLE_CULTURAL_SURVEY": True, "ENABLE_NATIVE_CULTURAL_SURVEY": False},
                [],
                False,
            ),
            (
                {"ENABLE_CULTURAL_SURVEY": True, "ENABLE_NATIVE_CULTURAL_SURVEY": False},
                [users_models.UserRole.BENEFICIARY],
                True,
            ),
            (
                {"ENABLE_CULTURAL_SURVEY": False, "ENABLE_NATIVE_CULTURAL_SURVEY": True},
                [],
                False,
            ),
            (
                {"ENABLE_CULTURAL_SURVEY": False, "ENABLE_NATIVE_CULTURAL_SURVEY": True},
                [users_models.UserRole.BENEFICIARY],
                True,
            ),
            (
                {"ENABLE_CULTURAL_SURVEY": False, "ENABLE_NATIVE_CULTURAL_SURVEY": False},
                [],
                False,
            ),
            (
                {"ENABLE_CULTURAL_SURVEY": False, "ENABLE_NATIVE_CULTURAL_SURVEY": False},
                [users_models.UserRole.BENEFICIARY],
                False,
            ),
        ],
    )
    def test_user_should_need_to_fill_cultural_survey(self, client, feature_flags, roles, needsToFillCulturalSurvey):
        user = users_factories.UserFactory(roles=roles)

        client.with_token(user.email)
        with override_features(**feature_flags):
            response = client.get("/native/v1/me")

        assert response.json["needsToFillCulturalSurvey"] == needsToFillCulturalSurvey

    def test_num_queries_with_next_step(self, client):
        user = users_factories.UserFactory(
            activity=users_models.ActivityEnum.STUDENT.value,
            dateOfBirth=datetime.utcnow() - relativedelta(years=18, days=5),
            email=self.identifier,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED],
        )
        client.with_token(user.email)

        response = client.get("/native/v1/me")
        assert response.status_code == 200
        client.with_token(user.email)
        n_queries = 1  # get user
        n_queries += 1  # get all feature flages
        n_queries += 1  # get bookings

        with testing.assert_num_queries(n_queries):
            response = client.get("/native/v1/me")

    def test_num_queries_beneficiary(self, client):
        user = users_factories.BeneficiaryGrant18Factory()

        client.with_token(user.email)

        response = client.get("/native/v1/me")
        assert response.status_code == 200
        client.with_token(user.email)

        with testing.assert_no_duplicated_queries():
            response = client.get("/native/v1/me")

    def should_hide_cultural_survey_if_not_beneficiary(self, client):
        user = users_factories.UserFactory(
            activity=users_models.ActivityEnum.STUDENT.value,
            dateOfBirth=datetime.utcnow() - relativedelta(years=18, days=5),
            email=self.identifier,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED],
        )
        client.with_token(user.email)

        response = client.get("/native/v1/me")
        assert response.status_code == 200
        assert response.json["needsToFillCulturalSurvey"] is False

    def should_display_cultural_survey_if_beneficiary(self, client):
        user = users_factories.BeneficiaryGrant18Factory()

        expected_num_queries = (
            5  # user + deposit + booking(from _get_booked_offers) + booking (from get_domains_credit) + feature
        )

        client.with_token(user.email)

        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/me")
            assert response.status_code == 200
        assert response.json["needsToFillCulturalSurvey"] is True

    def test_user_without_password(self, client):
        sso = users_factories.SingleSignOnFactory()
        user = sso.user
        user.password = None

        expected_num_queries = 5  # user(update) + user+ beneficiary_fraud_review + deposit + booking
        with assert_num_queries(expected_num_queries):
            response = client.with_token(user.email).get("/native/v1/me")
            assert response.status_code == 200, response.json

        assert response.json["hasPassword"] == False


class AccountCreationTest:
    identifier = "email@example.com"

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_account_creation(self, mocked_check_recaptcha_token_is_valid, client, app):
        assert users_models.User.query.first() is None
        data = {
            "email": "John.doe@example.com",
            "password": "Aazflrifaoi6@",
            "birthdate": "1960-12-31",
            "notifications": True,
            "token": "gnagna",
            "marketingEmailSubscription": True,
            "appsFlyerUserId": "apps_flyer_user_id",
            "appsFlyerPlatform": "iOS",
            "firebasePseudoId": "firebase_pseudo_id",
        }

        response = client.post("/native/v1/account", json=data)
        assert response.status_code == 204, response.json

        user = users_models.User.query.first()
        assert user is not None
        assert user.email == "john.doe@example.com"
        assert user.get_notification_subscriptions().marketing_email
        assert user.isEmailValidated is False
        assert user.checkPassword(data["password"])
        assert user.externalIds == {
            "apps_flyer": {"user": "apps_flyer_user_id", "platform": "IOS"},
            "firebase_pseudo_id": "firebase_pseudo_id",
        }

        mocked_check_recaptcha_token_is_valid.assert_called()
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(TransactionalEmail.EMAIL_CONFIRMATION.value)
        assert len(push_testing.requests) == 2
        assert len(users_testing.sendinblue_requests) == 1

        email_validation_token_exists = token_utils.Token.token_exists(token_utils.TokenType.EMAIL_VALIDATION, user.id)

        assert email_validation_token_exists

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_too_young_account_creation(self, mocked_check_recaptcha_token_is_valid, client):
        assert users_models.User.query.first() is None
        data = {
            "email": "John.doe@example.com",
            "password": "Aazflrifaoi6@",
            "birthdate": (datetime.utcnow() - relativedelta(years=15, days=-1)).date().isoformat(),
            "notifications": True,
            "token": "gnagna",
            "marketingEmailSubscription": True,
        }

        response = client.post("/native/v1/account", json=data)
        assert response.status_code == 400
        assert "dateOfBirth" in response.json
        assert not push_testing.requests

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_save_trusted_device(self, mocked_check_recaptcha_token_is_valid, client):
        data = {
            "email": "John.doe@example.com",
            "password": "Aazflrifaoi6@",
            "birthdate": "1960-12-31",
            "notifications": True,
            "token": "gnagna",
            "marketingEmailSubscription": True,
            "trustedDevice": {
                "deviceId": "2E429592-2446-425F-9A62-D6983F375B3B",
                "source": "iPhone 13",
                "os": "iOS",
            },
        }

        client.post("/native/v1/account", json=data)

        trusted_device = users_models.TrustedDevice.query.one()

        assert trusted_device.deviceId == data["trustedDevice"]["deviceId"]
        assert trusted_device.source == "iPhone 13"
        assert trusted_device.os == "iOS"

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def should_not_save_trusted_device_when_no_device_info(self, mocked_check_recaptcha_token_is_valid, client):
        data = {
            "email": "John.doe@example.com",
            "password": "Aazflrifaoi6@",
            "birthdate": "1960-12-31",
            "notifications": True,
            "token": "gnagna",
            "marketingEmailSubscription": True,
        }

        client.post("/native/v1/account", json=data)

        assert users_models.TrustedDevice.query.count() == 0

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    @override_features(WIP_ENABLE_TRUSTED_DEVICE=False)
    def should_not_save_trusted_device_when_feature_flag_is_disabled(
        self, mocked_check_recaptcha_token_is_valid, client
    ):
        data = {
            "email": "John.doe@example.com",
            "password": "Aazflrifaoi6@",
            "birthdate": "1960-12-31",
            "notifications": True,
            "token": "gnagna",
            "marketingEmailSubscription": True,
            "trustedDevice": {
                "deviceId": "2E429592-2446-425F-9A62-D6983F375B3B",
                "source": "iPhone 13",
                "os": "iOS",
            },
        }

        client.post("/native/v1/account", json=data)

        assert users_models.TrustedDevice.query.count() == 0

    def test_account_creation_with_weak_password(self, client):
        data = {
            "email": "John.doe@example.com",
            "password": "simple_password",
            "birthdate": "1960-12-31",
            "notifications": False,
            "token": "dummy token",
            "marketingEmailSubscription": False,
        }
        response = client.post("/native/v1/account", json=data)

        assert response.status_code == 400, response.json
        assert "password" in response.json


class AccountCreationEmailExistsTest:
    identifier = "email@example.com"

    @property
    def data(self):
        return {
            "email": self.identifier,
            "password": "Aazflrifaoi6@",
            "birthdate": "1960-12-31",
            "notifications": True,
            "token": "gnagna",
            "marketingEmailSubscription": True,
        }

    def assert_email_sent(self, response, user):
        """
        An email sent here implies:
            1. an OK http status code returned by the api
            2. an email with the right template
            3. a RESET_PASSWORD token created
        """
        assert response.status_code == 204, response.json

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(TransactionalEmail.EMAIL_ALREADY_EXISTS.value)

        assert token_utils.Token.token_exists(token_utils.TokenType.RESET_PASSWORD, user.id)

    def test_active_account(self, client):
        user = users_factories.UserFactory(email=self.identifier)

        response = client.post("/native/v1/account", json=self.data)
        self.assert_email_sent(response, user)

    def test_suspended_by_fraud_account(self, client):
        user = users_factories.UserFactory(email=self.identifier, isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, reason=users_constants.SuspensionReason.FRAUD_SUSPICION
        )

        response = client.post("/native/v1/account", json=self.data)
        self.assert_email_sent(response, user)

    def test_suspended_upon_user_request_account(self, client):
        user = users_factories.UserFactory(email=self.identifier, isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )

        response = client.post("/native/v1/account", json=self.data)
        self.assert_email_sent(response, user)

    def test_deleted_account(self, client):
        user = users_factories.UserFactory(email=self.identifier, isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(user=user, reason=users_constants.SuspensionReason.DELETED)

        response = client.post("/native/v1/account", json=self.data)
        self.assert_email_sent(response, user)

    def test_email_exists_but_not_validated(self, client):
        user = users_factories.UserFactory(email=self.identifier, isEmailValidated=False)
        token_utils.Token.create(
            type_=token_utils.TokenType.EMAIL_VALIDATION,
            ttl=users_constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME,
            user_id=user.id,
        )
        response = client.post("/native/v1/account", json=self.data)
        self.assert_email_sent(response, user)


class AccountCreationWithSSOTest:
    google_user = GoogleUser(sub="google_user_identifier", email="docteur.cuesta@passculture.app", email_verified=True)

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_account_creation_and_login(self, mocked_check_recaptcha_token_is_valid, client):
        account_creation_token = token_utils.UUIDToken.create(
            token_utils.TokenType.ACCOUNT_CREATION,
            users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME,
            data=self.google_user.model_dump(),
        )

        response = client.post(
            "/native/v1/oauth/google/account",
            json={
                "accountCreationToken": account_creation_token.encoded_token,
                "birthdate": "1960-12-31",
                "notifications": True,
                "token": "recaptcha token",
                "marketingEmailSubscription": True,
                "appsFlyerUserId": "apps_flyer_user_id",
                "appsFlyerPlatform": "iOS",
                "firebasePseudoId": "firebase_pseudo_id",
            },
        )

        assert response.status_code == 200, response.json
        assert "accessToken" in response.json
        assert "refreshToken" in response.json
        assert response.json["accountState"] == users_models.AccountState.ACTIVE.value

        user = users_models.User.query.one()
        assert user is not None
        assert user.email == "docteur.cuesta@passculture.app"
        assert user.get_notification_subscriptions().marketing_email
        assert user.isEmailValidated
        assert user.password is None
        assert user.externalIds == {
            "apps_flyer": {"user": "apps_flyer_user_id", "platform": "IOS"},
            "firebase_pseudo_id": "firebase_pseudo_id",
        }

        mocked_check_recaptcha_token_is_valid.assert_called()
        assert len(mails_testing.outbox) == 0  # no email verification
        assert len(push_testing.requests) == 2
        assert len(users_testing.sendinblue_requests) == 1

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_account_already_present(self, mocked_check_recaptcha_token_is_valid, client):
        users_factories.UserFactory(email="docteur.cuesta@passculture.app")
        account_creation_token = token_utils.UUIDToken.create(
            token_utils.TokenType.ACCOUNT_CREATION,
            users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME,
            data=self.google_user.model_dump(),
        )

        response = client.post(
            "/native/v1/oauth/google/account",
            json={
                "accountCreationToken": account_creation_token.encoded_token,
                "birthdate": (datetime.utcnow() - relativedelta(years=15, days=-1)).date().isoformat(),
                "notifications": True,
                "token": "gnagna",
                "marketingEmailSubscription": True,
            },
        )

        assert response.status_code == 400
        assert "email" in response.json
        assert users_models.User.query.filter(users_models.User.email == "docteur.cuesta@passculture.app").count() == 1

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_too_young_account_creation(self, mocked_check_recaptcha_token_is_valid, client):
        account_creation_token = token_utils.UUIDToken.create(
            token_utils.TokenType.ACCOUNT_CREATION,
            users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME,
            data=self.google_user.model_dump(),
        )

        response = client.post(
            "/native/v1/oauth/google/account",
            json={
                "accountCreationToken": account_creation_token.encoded_token,
                "birthdate": (datetime.utcnow() - relativedelta(years=15, days=-1)).date().isoformat(),
                "notifications": True,
                "token": "gnagna",
                "marketingEmailSubscription": True,
            },
        )

        assert response.status_code == 400
        assert "dateOfBirth" in response.json
        assert not push_testing.requests

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_save_trusted_device(self, mocked_check_recaptcha_token_is_valid, client):
        account_creation_token = token_utils.UUIDToken.create(
            token_utils.TokenType.ACCOUNT_CREATION,
            users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME,
            data=self.google_user.model_dump(),
        )

        response = client.post(
            "/native/v1/oauth/google/account",
            json={
                "accountCreationToken": account_creation_token.encoded_token,
                "birthdate": "1960-12-31",
                "notifications": True,
                "token": "gnagna",
                "marketingEmailSubscription": True,
                "trustedDevice": {
                    "deviceId": "2E429592-2446-425F-9A62-D6983F375B3B",
                    "source": "iPhone 13",
                    "os": "iOS",
                },
            },
        )

        assert response.status_code == 200, response.json

        trusted_device = users_models.TrustedDevice.query.one()
        assert trusted_device.deviceId == "2E429592-2446-425F-9A62-D6983F375B3B"
        assert trusted_device.source == "iPhone 13"
        assert trusted_device.os == "iOS"

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def should_not_save_trusted_device_when_no_device_info(self, mocked_check_recaptcha_token_is_valid, client):
        account_creation_token = token_utils.UUIDToken.create(
            token_utils.TokenType.ACCOUNT_CREATION,
            users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME,
            data=self.google_user.model_dump(),
        )

        response = client.post(
            "/native/v1/oauth/google/account",
            json={
                "accountCreationToken": account_creation_token.encoded_token,
                "birthdate": "1960-12-31",
                "notifications": True,
                "token": "gnagna",
                "marketingEmailSubscription": True,
            },
        )

        assert response.status_code == 200, response.json
        assert users_models.TrustedDevice.query.count() == 0

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_account_creation_token_past_expiration_date(self, mocked_check_recaptcha_token_is_valid, client):
        with time_machine.travel("2022-01-01"):
            account_creation_token = token_utils.UUIDToken.create(
                token_utils.TokenType.ACCOUNT_CREATION,
                users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME,
                data=self.google_user.model_dump(),
            )

        response = client.post(
            "/native/v1/oauth/google/account",
            json={
                "accountCreationToken": account_creation_token.encoded_token,
                "birthdate": "1960-12-31",
                "notifications": True,
                "token": "gnagna",
                "marketingEmailSubscription": True,
            },
        )

        assert response.status_code == 400, response.json
        assert response.json["code"] == "SSO_ACCOUNT_CREATION_TIMEOUT"

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_account_creation_token_already_expired(self, mocked_check_recaptcha_token_is_valid, client):
        account_creation_token = token_utils.UUIDToken.create(
            token_utils.TokenType.ACCOUNT_CREATION,
            users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME,
            data=self.google_user.model_dump(),
        )
        account_creation_token.expire()

        response = client.post(
            "/native/v1/oauth/google/account",
            json={
                "accountCreationToken": account_creation_token.encoded_token,
                "birthdate": "1960-12-31",
                "notifications": True,
                "token": "gnagna",
                "marketingEmailSubscription": True,
            },
        )

        assert response.status_code == 400, response.json
        assert response.json["code"] == "SSO_INVALID_ACCOUNT_CREATION"

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_account_creation_expires_token(self, mocked_check_recaptcha_token_is_valid, client):
        account_creation_token = token_utils.UUIDToken.create(
            token_utils.TokenType.ACCOUNT_CREATION,
            users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME,
            data=self.google_user.model_dump(),
        )

        response = client.post(
            "/native/v1/oauth/google/account",
            json={
                "accountCreationToken": account_creation_token.encoded_token,
                "birthdate": "1960-12-31",
                "notifications": True,
                "token": "gnagna",
                "marketingEmailSubscription": True,
            },
        )

        assert response.status_code == 200, response.json
        assert not token_utils.UUIDToken.token_exists(
            token_utils.TokenType.ACCOUNT_CREATION, account_creation_token.key_suffix
        )

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    @patch("pcapi.core.subscription.dms.api.try_dms_orphan_adoption")
    def test_adopt_dms_application(self, try_dms_orphan_adoption_mock, mocked_check_recaptcha_token_is_valid, client):
        account_creation_token = token_utils.UUIDToken.create(
            token_utils.TokenType.ACCOUNT_CREATION,
            users_constants.ACCOUNT_CREATION_TOKEN_LIFE_TIME,
            data=self.google_user.model_dump(),
        )

        response = client.post(
            "/native/v1/oauth/google/account",
            json={
                "accountCreationToken": account_creation_token.encoded_token,
                "birthdate": "1960-12-31",
                "notifications": True,
                "token": "gnagna",
                "marketingEmailSubscription": True,
            },
        )

        user = users_models.User.query.one()

        assert response.status_code == 200, response.json
        try_dms_orphan_adoption_mock.assert_called_once_with(user)


class UserProfileUpdateTest:
    identifier = "email@example.com"

    def test_update_user_profile(self, app, client):
        password = "some_random_string"
        user = users_factories.UserFactory(email=self.identifier, password=password)

        client.with_token(user.email)
        response = client.patch(
            "/native/v1/profile",
            json={
                "subscriptions": {"marketingPush": True, "marketingEmail": False, "subscribedThemes": ["cinema"]},
            },
        )

        assert response.status_code == 200

        user = users_models.User.query.filter_by(email=self.identifier).first()

        assert user.get_notification_subscriptions().marketing_push
        assert not user.get_notification_subscriptions().marketing_email
        assert user.get_notification_subscriptions().subscribed_themes == ["cinema"]
        assert len(push_testing.requests) == 2

    def test_unsubscribe_push_notifications(self, client, app):
        user = users_factories.UserFactory(email=self.identifier)

        client.with_token(email=self.identifier)
        response = client.patch(
            "/native/v1/profile",
            json={"subscriptions": {"marketingPush": False, "marketingEmail": False, "subscribedThemes": []}},
        )

        assert response.status_code == 200

        user = users_models.User.query.filter_by(email=self.identifier).first()
        assert not user.get_notification_subscriptions().marketing_push
        assert not user.get_notification_subscriptions().marketing_email

        android_batch_request = push_testing.requests[0]
        ios_batch_request = push_testing.requests[1]
        android_batch_attributes = android_batch_request.get("attribute_values", {})
        ios_batch_attributes = ios_batch_request.get("attribute_values", {})

        assert android_batch_request.get("user_id") == user.id
        assert android_batch_attributes.get("u.marketing_push_subscription") is False
        assert android_batch_attributes.get("u.marketing_email_subscription") is False
        assert android_batch_attributes.get("ut.permanent_theme_preference") is None
        assert ios_batch_request.get("user_id") == user.id
        assert ios_batch_attributes.get("u.marketing_push_subscription") is False
        assert ios_batch_attributes.get("u.marketing_email_subscription") is False
        assert ios_batch_attributes.get("ut.permanent_theme_preference") is None

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.authorUser == user
        assert action.user == user
        assert action.extraData == {
            "modified_info": {
                "notificationSubscriptions.marketing_email": {"old_info": True, "new_info": False},
                "notificationSubscriptions.marketing_push": {"old_info": True, "new_info": False},
            }
        }

    def test_subscription_logging_to_data(self, client, caplog):
        users_factories.UserFactory(
            email=self.identifier,
            notificationSubscriptions={
                "marketing_push": True,
                "marketing_email": True,
                "subscribed_themes": ["musique", "visites"],
            },
        )

        with caplog.at_level(logging.INFO):
            client.with_token(email=self.identifier)
            response = client.patch(
                "/native/v1/profile",
                json={
                    "subscriptions": {
                        "marketingPush": True,
                        "marketingEmail": False,
                        "subscribedThemes": ["visites", "cinema"],
                    },
                    "origin": "profile",
                },
            )

        assert response.status_code == 200
        assert caplog.records[0].extra == {
            "newlySubscribedTo": {"email": False, "push": False, "themes": {"cinema"}},
            "newlyUnsubscribedFrom": {"email": True, "push": False, "themes": {"musique"}},
            "subscriptions": {
                "marketing_push": True,
                "marketing_email": False,
                "subscribed_themes": ["visites", "cinema"],
            },
            "analyticsSource": "app-native",
            "origin": "profile",
        }
        assert caplog.records[0].technical_message_id == "subscription_update"

    def test_postal_code_update(self, client):
        user = users_factories.UserFactory(email=self.identifier)

        client.with_token(email=self.identifier)
        response = client.patch("/native/v1/profile", json={"postalCode": "38000", "city": "Grenoble"})

        assert response.status_code == 200
        assert user.postalCode == "38000"
        assert user.city == "Grenoble"

    def test_activity_update(self, client):
        user = users_factories.UserFactory(email=self.identifier)

        client.with_token(email=self.identifier)
        response = client.patch("/native/v1/profile", json={"activity_id": users_models.ActivityEnum.UNEMPLOYED.name})

        assert response.status_code == 200
        assert user.activity == users_models.ActivityEnum.UNEMPLOYED.value

    def test_empty_patch(self, client):
        user = users_factories.UserFactory(
            email=self.identifier,
            activity=users_models.ActivityEnum.UNEMPLOYED.value,
            city="Grenoble",
            postalCode="38000",
            notificationSubscriptions={
                "marketing_push": True,
                "marketing_email": True,
                "subscribed_themes": ["musique", "visites"],
            },
        )

        client.with_token(email=self.identifier)
        response = client.patch("/native/v1/profile", json={})

        assert response.status_code == 200
        assert user.activity == users_models.ActivityEnum.UNEMPLOYED.value
        assert user.city == "Grenoble"
        assert user.postalCode == "38000"
        assert user.notificationSubscriptions == {
            "marketing_push": True,
            "marketing_email": True,
            "subscribed_themes": ["musique", "visites"],
        }


class ResetRecreditAmountToShow:
    def test_update_user_profile_reset_recredit_amount_to_show(self, client, app):
        user = users_factories.UnderageBeneficiaryFactory(email=self.identifier, recreditAmountToShow=30)

        client.with_token(email=self.identifier)
        response = client.post("/native/v1/reset_recredit_amount_to_show")

        assert response.status_code == 200
        assert user.recreditAmountToShow is None


class ConfirmUpdateUserEmailTest:
    def _initialize_token(self, user, app, new_email):
        return token_utils.Token.create(
            type_=token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION,
            ttl=users_constants.EMAIL_CHANGE_TOKEN_LIFE_TIME,
            user_id=user.id,
            data={"new_email": new_email},
        ).encoded_token

    def test_can_confirm_email_update(self, client, app):
        user = users_factories.BeneficiaryGrant18Factory()
        email_update_request = users_factories.EmailUpdateEntryFactory(user=user)
        token = self._initialize_token(user, app, email_update_request.newEmail)

        client.with_token(user.email)
        response = client.post("/native/v1/profile/email_update/confirm", json={"token": token})

        assert response.status_code == 204
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["params"]["FIRSTNAME"] == user.firstName

        validation_email = mails_testing.outbox[-1]
        validation_link = urlparse(validation_email["params"]["CONFIRMATION_LINK"])
        base_url = parse_qs(validation_link.query)["link"][0]
        base_url_params = parse_qs(urlparse(base_url).query)

        assert {"new_email", "token", "expiration_timestamp"} <= base_url_params.keys()
        assert base_url_params["new_email"] == [email_update_request.newEmail]

    mock_redis_client = fakeredis.FakeStrictRedis()

    def test_cannot_confirm_after_expiration(self, client, app):
        user = users_factories.BeneficiaryGrant18Factory()
        email_update_request = users_factories.EmailUpdateEntryFactory(user=user)
        with mock.patch("flask.current_app.redis_client", self.mock_redis_client):
            with time_machine.travel("2021-01-01"):
                token = self._initialize_token(user, app, email_update_request.newEmail)
            with time_machine.travel("2021-01-02"):
                client.with_token(user.email)
                response = client.post("/native/v1/profile/email_update/confirm", json={"token": token})
                assert response.status_code == 401
                assert response.json["message"] == "aucune demande de changement d'email en cours"

    def test_cannot_confirm_if_no_pending_email_update(self, client, app):
        user = users_factories.BeneficiaryGrant18Factory()
        expiration_date = datetime.utcnow() + users_constants.EMAIL_CHANGE_TOKEN_LIFE_TIME
        token = encode_jwt_payload({"current_email": user.email, "new_email": "exemple@exemple.com"}, expiration_date)

        client.with_token(user.email)
        response = client.post("/native/v1/profile/email_update/confirm", json={"token": token})

        assert response.status_code == 401
        assert response.json["message"] == "aucune demande de changement d'email en cours"


class UpdateUserEmailTest:
    identifier = "email@example.com"

    def test_update_user_email(self, app, client):
        new_email = "updated_" + self.identifier
        password = "some_random_string"
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier, password=password)

        client.with_token(user.email)
        response = client.post(
            "/native/v1/profile/update_email",
            json={
                "email": new_email,
                "password": password,
            },
        )

        assert response.status_code == 204

        user = users_models.User.query.filter_by(email=self.identifier).first()
        assert user.email == self.identifier  # email not updated until validation link is used
        assert len(mails_testing.outbox) == 1  # one confirmation email to the current address

        # extract new email from activation link, which is a firebase
        # dynamic link meaning that the real url needs to be extracted
        # from it.
        activation_email = mails_testing.outbox[-1]
        confirmation_link = urlparse(activation_email["params"]["CONFIRMATION_LINK"])
        base_url = parse_qs(confirmation_link.query)["link"][0]
        base_url_params = parse_qs(urlparse(base_url).query)

        assert {"new_email", "token", "expiration_timestamp"} <= base_url_params.keys()
        assert base_url_params["new_email"] == [new_email]

    def test_update_email_user_not_connected(self, app, client):
        new_email = "updated_" + self.identifier
        password = "some_random_string"
        response = client.post(
            "/native/v1/profile/update_email",
            json={
                "email": new_email,
                "password": password,
            },
        )
        assert response.status_code == 401

    def test_update_email_missing_password(self, app, client):
        user = users_factories.UserFactory(email=self.identifier)

        client.with_token(user.email)
        response = client.post(
            "/native/v1/profile/update_email",
            json={
                "email": "updated_" + self.identifier,
            },
        )

        assert response.status_code == 400
        assert "password" in response.json

        assert user.email == self.identifier
        assert not mails_testing.outbox  # missing password => no update, no email sent

    @pytest.mark.parametrize(
        "email,password,response_status,expected_error_code,expected_error_message,email_sent",
        [
            ("not_an_email", "not_the_users_password", 400, None, None, []),
            (
                "used_email@example.com",
                "not_the_users_password",
                account_errors.WrongPasswordError.status_code,
                account_errors.WrongPasswordError().errors["error_code"],
                account_errors.WrongPasswordError().errors["message"],
                [],
            ),
            ("used_email@example.com", "this_is_the_users_password", 204, None, None, []),
        ],
    )
    def test_update_email_erros(
        self, client, app, email, password, response_status, expected_error_code, expected_error_message, email_sent
    ):
        users_factories.UserFactory(email="used_email@example.com")
        user = users_factories.UserFactory(email=self.identifier, password="this_is_the_users_password")

        client.with_token(user.email)
        response = client.post(
            "/native/v1/profile/update_email",
            json={
                "email": email,
                "password": password,
            },
        )

        assert response.status_code == response_status
        if expected_error_code:
            assert response.json["error_code"] == expected_error_code
        if expected_error_message:
            assert response.json["message"] == expected_error_message

        user = users_models.User.query.filter_by(email=self.identifier).first()
        assert user.email == self.identifier
        assert mails_testing.outbox == email_sent

    @override_settings(MAX_EMAIL_UPDATE_ATTEMPTS=1)
    @patch("pcapi.core.users.email.update.check_no_ongoing_email_update_request")
    def test_update_email_too_many_attempts(self, _mock, client):
        """
        Test that a user cannot request more than
        MAX_EMAIL_UPDATE_ATTEMPTS email update change within the last
        N days.
        """
        password = "some_random_string"
        user = users_factories.UserFactory(email=self.identifier, password=password)

        client.with_token(user.email)
        response = client.post(
            "/native/v1/profile/update_email",
            json={
                "email": "updated_once_" + user.email,
                "password": password,
            },
        )
        assert response.status_code == 204
        response = client.post(
            "/native/v1/profile/update_email",
            json={
                "email": "updated_twice_" + user.email,
                "password": password,
            },
        )

        assert response.status_code == 400
        assert response.json["error_code"] == account_errors.EMAIL_UPDATE_LIMIT.code
        assert response.json["message"] == account_errors.EMAIL_UPDATE_LIMIT.message

    def test_ongoing_email_update_blocks_the_next_update_request(self, client):
        password = "some_random_string"
        user = users_factories.UserFactory(email=self.identifier, password=password)
        client.with_token(user.email)

        first_response = client.post(
            "/native/v1/profile/update_email",
            json={
                "email": "updated_" + user.email,
                "password": password,
            },
        )
        assert first_response.status_code == 204

        client.with_token(user.email)
        second_response = client.post(
            "/native/v1/profile/update_email",
            json={
                "email": "updated_twice_" + user.email,
                "password": password,
            },
        )

        assert second_response.status_code == 400
        assert second_response.json["error_code"] == account_errors.EMAIL_UPDATE_PENDING.code
        assert second_response.json["message"] == account_errors.EMAIL_UPDATE_PENDING.message

    def test_end_to_end_update_email(self, client):
        password = "some_random_string"
        old_email = self.identifier
        new_email = "updated_" + old_email
        user = users_factories.UserFactory(email=old_email, password=password)

        # User requests email update
        client.with_token(user.email)
        response = client.post(
            "/native/v1/profile/update_email",
            json={
                "email": new_email,
                "password": password,
            },
        )
        assert response.status_code == 204

        # User receives an email to his current email asking to confirm that he wants to change email or to cancel if he is not the one who requested it
        assert mails_testing.outbox
        confirmation_email = mails_testing.outbox[-1]
        assert confirmation_email["To"] == old_email
        confirmation_link = urlparse(confirmation_email["params"]["CONFIRMATION_LINK"])
        cancellation_link = urlparse(confirmation_email["params"]["CANCELLATION_LINK"])
        base_url_confirmation = parse_qs(confirmation_link.query)["link"][0]
        base_url_cancellation = parse_qs(cancellation_link.query)["link"][0]
        base_url_params_confirmation = parse_qs(urlparse(base_url_confirmation).query)
        base_url_params_cancellation = parse_qs(urlparse(base_url_cancellation).query)
        assert {"new_email", "token", "expiration_timestamp"} <= base_url_params_confirmation.keys()
        assert {"new_email", "token", "expiration_timestamp"} <= base_url_params_cancellation.keys()
        assert base_url_params_confirmation["new_email"] == [new_email]
        assert base_url_params_cancellation["new_email"] == [new_email]
        assert base_url_params_cancellation["token"] == base_url_params_confirmation["token"]

        # the email doesn't change yet
        user = users_models.User.query.get(user.id)
        assert user.email == old_email

        # We record the email update request in the user's email history
        assert user.email_history[-1].eventType == users_models.EmailHistoryEventTypeEnum.UPDATE_REQUEST

        # User confirms (from the link sent to their current e-mail address)
        response = client.post(
            "/native/v1/profile/email_update/confirm",
            json={
                "token": base_url_params_confirmation["token"][0],
            },
        )
        assert response.status_code == 204

        # User receives an e-mail on their new e-mail address, asking to follow a link to validate the change.
        # This email is sent to check that the user has access to the new email address.
        validation_email = mails_testing.outbox[-1]
        assert validation_email["To"] == new_email
        validation_link = urlparse(validation_email["params"]["CONFIRMATION_LINK"])
        base_url_validation = parse_qs(validation_link.query)["link"][0]
        base_url_params_validation = parse_qs(urlparse(base_url_validation).query)
        assert {"new_email", "token", "expiration_timestamp"} <= base_url_params_validation.keys()
        assert base_url_params_validation["new_email"] == [new_email]

        # the email doesn't change yet
        user = users_models.User.query.get(user.id)
        assert user.email == old_email

        # We record the email update request in the user's email history
        assert user.email_history[-1].eventType == users_models.EmailHistoryEventTypeEnum.CONFIRMATION

        # User validates (from the link sent to their new e-mail address)
        response = client.put(
            "/native/v1/profile/email_update/validate",
            json={
                "token": base_url_params_validation["token"][0],
            },
        )
        assert response.status_code == 200
        # Ensure the access token is valid
        access_token = response.json["accessToken"]

        expected_num_query = 4  # user + beneficiary_fraud_review + deposit + booking

        client.auth_header = {"Authorization": f"Bearer {access_token}"}
        with assert_num_queries(expected_num_query):
            protected_response = client.get("/native/v1/me")
            assert protected_response.status_code == 200

        # Ensure the refresh token is valid
        refresh_token = response.json["refreshToken"]
        client.auth_header = {"Authorization": f"Bearer {refresh_token}"}
        refresh_response = client.post("/native/v1/refresh_access_token", json={})
        assert refresh_response.status_code == 200

        # the email changes
        user = users_models.User.query.get(user.id)
        assert user.email == new_email

        # The user receives an email on their new email address informing him of the email change
        assert len(mails_testing.outbox) == 3
        assert mails_testing.outbox[-1]["To"] == new_email

        # We record the email validation in the user's email history
        assert user.email_history[-1].eventType == users_models.EmailHistoryEventTypeEnum.VALIDATION

    def test_end_to_end_update_email_with_cancellation(self, client):
        password = "some_random_string"
        old_email = self.identifier
        new_email = "updated_" + old_email
        user = users_factories.UserFactory(email=old_email, password=password)
        client.with_token(user.email)

        # User requests email update
        response = client.post(
            "/native/v1/profile/update_email",
            json={
                "email": new_email,
                "password": password,
            },
        )
        assert response.status_code == 204

        # User receives an email to his current email asking to confirm that he wants to change email or to cancel if he is not the one who requested it
        assert mails_testing.outbox
        confirmation_email = mails_testing.outbox[-1]
        assert confirmation_email["To"] == old_email
        confirmation_link = urlparse(confirmation_email["params"]["CONFIRMATION_LINK"])
        cancellation_link = urlparse(confirmation_email["params"]["CANCELLATION_LINK"])
        base_url_confirmation = parse_qs(confirmation_link.query)["link"][0]
        base_url_cancellation = parse_qs(cancellation_link.query)["link"][0]
        base_url_params_confirmation = parse_qs(urlparse(base_url_confirmation).query)
        base_url_params_cancellation = parse_qs(urlparse(base_url_cancellation).query)
        assert {"new_email", "token", "expiration_timestamp"} <= base_url_params_confirmation.keys()
        assert {"new_email", "token", "expiration_timestamp"} <= base_url_params_cancellation.keys()
        assert base_url_params_confirmation["new_email"] == [new_email]
        assert base_url_params_cancellation["new_email"] == [new_email]
        assert base_url_params_cancellation["token"] == base_url_params_confirmation["token"]

        # the email doesn't change yet
        user = users_models.User.query.get(user.id)
        assert user.email == old_email

        # We record the email update request in the user's email history
        assert user.email_history[-1].eventType == users_models.EmailHistoryEventTypeEnum.UPDATE_REQUEST

        # User cancels (from the link sent to their current e-mail address)
        response = client.post(
            "/native/v1/profile/email_update/cancel",
            json={
                "token": base_url_params_confirmation["token"][0],
            },
        )

        assert response.status_code == 204

        # the email doesn't change
        user = users_models.User.query.get(user.id)
        assert user.email == old_email

        # User account is suspended
        assert not user.isActive

        # User receives an e-mail on their current email adress confirming the account suspenssion
        assert len(mails_testing.outbox) == 2
        assert mails_testing.outbox[-1]["To"] == old_email

        # We record the email cancellation in the user's email history
        assert user.email_history[-1].eventType == users_models.EmailHistoryEventTypeEnum.CANCELLATION


class GetEMailUpdateStatusTest:
    old_email = "old@email.com"
    new_email = "new@email.com"

    def test_can_retrieve_email_update_status(self, client):
        user = users_factories.UserFactory(email=self.old_email)
        request_email_update_with_credentials(user, self.new_email, settings.TEST_DEFAULT_PASSWORD)

        client = client.with_token(user.email)
        expected_num_queries = 2  # user + user_email_history
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/profile/email_update/status")
            assert response.status_code == 200

        assert response.json["newEmail"] == self.new_email
        assert response.json["expired"] is False
        assert response.json["status"] == users_models.EmailHistoryEventTypeEnum.UPDATE_REQUEST.value

    def test_with_no_email_update_event(self, client):
        user = users_factories.UserFactory(email=self.old_email)

        client = client.with_token(user.email)
        expected_num_queries = 2  # user + user_email_history
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/profile/email_update/status")
            assert response.status_code == 404

    def test_expired_token_is_reported(self, app, client):
        user = users_factories.UserFactory(email=self.old_email)
        request_email_update_with_credentials(user, self.new_email, settings.TEST_DEFAULT_PASSWORD)

        client = client.with_token(user.email)
        expected_num_queries = 2  # user + user_email_history

        with mock.patch.object(app.redis_client, "ttl", return_value=-1):
            with assert_num_queries(expected_num_queries):
                response = client.get("/native/v1/profile/email_update/status")
                assert response.status_code == 200

        assert response.json["newEmail"] == self.new_email
        assert response.json["expired"] is True
        assert response.json["status"] == users_models.EmailHistoryEventTypeEnum.UPDATE_REQUEST.value

    def test_assume_expired_if_no_token_expiration(self, app, client):
        user = users_factories.UserFactory(email=self.old_email)
        request_email_update_with_credentials(user, self.new_email, settings.TEST_DEFAULT_PASSWORD)

        redis_key = token_utils.Token.get_redis_key(token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION, user.id)
        redis_value = app.redis_client.get(redis_key)
        redis_expiration = app.redis_client.ttl(redis_key)
        app.redis_client.delete(redis_key)

        client = client.with_token(user.email)
        expected_num_queries = 2  # user + user_email_history
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/profile/email_update/status")
        app.redis_client.set(redis_key, redis_value)
        app.redis_client.expireat(redis_key, redis_expiration)

        assert response.status_code == 200
        assert response.json["newEmail"] == self.new_email
        assert response.json["expired"] is True
        assert response.json["status"] == users_models.EmailHistoryEventTypeEnum.UPDATE_REQUEST.value

    def test_get_active_token_expiration_no_token(
        self,
    ):
        assert email_update.get_active_token_expiration(users_factories.UserFactory()) is None

    def test_get_active_token_expiration_confirmation_token(
        self,
    ):
        user = users_factories.UserFactory()
        token_utils.Token.create(
            type_=token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION,
            ttl=users_constants.EMAIL_CHANGE_TOKEN_LIFE_TIME,
            user_id=user.id,
            data={"new_email": "new_email@email.com"},
        )
        assert email_update.get_active_token_expiration(user) is not None

    def test_get_active_token_expiration_validation_token(
        self,
    ):  # this is unit test should be moved to test_update.py inside core
        user = users_factories.UserFactory()
        token_utils.Token.create(
            type_=token_utils.TokenType.EMAIL_CHANGE_VALIDATION,
            ttl=users_constants.EMAIL_CHANGE_TOKEN_LIFE_TIME,
            user_id=user.id,
            data={"new_email": "new_email"},
        )
        assert email_update.get_active_token_expiration(user) is not None


class ValidateEmailTest:
    old_email = "old@email.com"
    new_email = "new@email.com"
    mock_redis_client = fakeredis.FakeStrictRedis()

    def _initialize_token(self, user, app, new_email):
        return token_utils.Token.create(
            type_=token_utils.TokenType.EMAIL_CHANGE_VALIDATION,
            ttl=users_constants.EMAIL_CHANGE_TOKEN_LIFE_TIME,
            user_id=user.id,
            data={"new_email": new_email},
        ).encoded_token

    def test_validate_email(self, app, client):
        user = users_factories.UserFactory(email=self.old_email)
        token = self._initialize_token(user, app, self.new_email)
        response = client.put("/native/v1/profile/email_update/validate", json={"token": token})

        assert response.status_code == 200
        # Ensure the access token is valid
        access_token = response.json["accessToken"]
        client.auth_header = {"Authorization": f"Bearer {access_token}"}

        protected_response = client.get("/native/v1/me")
        assert protected_response.status_code == 200

        # Ensure the refresh token is valid
        refresh_token = response.json["refreshToken"]
        client.auth_header = {"Authorization": f"Bearer {refresh_token}"}
        refresh_response = client.post("/native/v1/refresh_access_token", json={})
        assert refresh_response.status_code == 200

        user = users_models.User.query.get(user.id)
        assert user.email == self.new_email

    @patch("pcapi.core.subscription.dms.api.try_dms_orphan_adoption")
    def test_dms_adoption_on_email_validation_for_eligible_user(self, try_dms_orphan_adoption_mock, app, client):
        user = users_factories.UserFactory(
            email=self.old_email, dateOfBirth=datetime.utcnow() - relativedelta(years=18)
        )
        token = self._initialize_token(user, app, self.new_email)
        response = client.put("/native/v1/profile/email_update/validate", json={"token": token})

        assert response.status_code == 200
        try_dms_orphan_adoption_mock.assert_called_once_with(user)

    @patch("pcapi.core.subscription.dms.api.try_dms_orphan_adoption")
    def test_no_dms_adoption_on_email_validation_for_beneficiary_user(self, try_dms_orphan_adoption_mock, app, client):
        user = users_factories.UserFactory(email=self.old_email, roles=[users_models.UserRole.BENEFICIARY])
        token = self._initialize_token(user, app, self.new_email)
        response = client.put("/native/v1/profile/email_update/validate", json={"token": token})

        assert response.status_code == 200
        try_dms_orphan_adoption_mock.assert_not_called()

    def test_email_exists(self, app, client):
        """
        Test that if the email already exists, an OK response is sent
        but nothing is changed (avoid user enumeration).
        """
        user = users_factories.UserFactory(email=self.old_email)
        users_factories.UserFactory(email=self.new_email, isEmailValidated=True)
        token = self._initialize_token(user, app, self.new_email)
        response = client.put("/native/v1/profile/email_update/validate", json={"token": token})

        assert response.status_code == 200
        # Ensure the access token is valid
        access_token = response.json["accessToken"]
        client.auth_header = {"Authorization": f"Bearer {access_token}"}
        protected_response = client.get("/native/v1/me")
        assert protected_response.status_code == 200

        # Ensure the refresh token is valid
        refresh_token = response.json["refreshToken"]
        client.auth_header = {"Authorization": f"Bearer {refresh_token}"}
        refresh_response = client.post("/native/v1/refresh_access_token", json={})
        assert refresh_response.status_code == 200

        user = users_models.User.query.get(user.id)
        assert user.email == self.old_email

    def test_expired_token(self, app, client):
        user = users_factories.UserFactory(email=self.old_email)
        users_factories.UserFactory(email=self.new_email, isEmailValidated=True)
        with mock.patch("flask.current_app.redis_client", self.mock_redis_client):
            with time_machine.travel("2021-01-01 00:00:00"):
                token = self._initialize_token(user, app, self.new_email)
            with time_machine.travel("2021-01-03 00:00:00"):
                response = client.put("/native/v1/profile/email_update/validate", json={"token": token})
                assert response.status_code == 400
                assert response.json["code"] == "INVALID_TOKEN"

                user = users_models.User.query.get(user.id)
                assert user.email == self.old_email


class CancelEmailChangeTest:
    def _initialize_token(self, user):
        return token_utils.Token.create(
            type_=token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION,
            ttl=users_constants.EMAIL_CHANGE_TOKEN_LIFE_TIME,
            user_id=user.id,
            data={"new_email": "example@example.com"},
        ).encoded_token

    def test_cancel_email_change(self, app, client):
        user = users_factories.UserFactory()
        token = self._initialize_token(user)

        response = client.post("/native/v1/profile/email_update/cancel", json={"token": token})
        assert response.status_code == 204
        assert not token_utils.Token.token_exists(token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION, user.id)
        assert mails_testing.outbox[0]["params"]["FIRSTNAME"] == user.firstName
        assert get_email_update_latest_event(user).eventType == users_models.EmailHistoryEventTypeEnum.CANCELLATION
        assert user.account_state == users_models.AccountState.SUSPENDED

    mock_redis_client = fakeredis.FakeStrictRedis()

    def test_cancel_email_change_expired_token(self, app, client):
        with mock.patch("flask.current_app.redis_client", self.mock_redis_client):
            with time_machine.travel("2021-01-01"):
                user = users_factories.UserFactory()
                token = self._initialize_token(user)
            with time_machine.travel("2021-01-02"):
                response = client.post("/native/v1/profile/email_update/cancel", json={"token": token})
                assert response.status_code == 401


class GetTokenExpirationTest:
    email = "some@email.com"

    @time_machine.travel("2021-01-01", tick=False)
    def test_token_expiration(self, app, client):
        """
        Setup the active token key with a TTL. Then test that the route
        returns the expected expiration datetime, with a little error
        margin: datetimes and redis commands do not have the same time
        precision (ms vs s) which causes some little difference when
        deserializing the redis ttl. Note that we absolutely don't need
        a ms precision here.
        """
        user = users_factories.UserFactory(email=self.email)
        expiration_date = datetime.utcnow() + users_constants.EMAIL_CHANGE_TOKEN_LIFE_TIME
        token_utils.Token.create(
            type_=token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION,
            ttl=users_constants.EMAIL_CHANGE_TOKEN_LIFE_TIME,
            user_id=user.id,
            data={"new_email": "newemail@email.com"},
        )

        client = client.with_token(user.email)
        expected_num_queries = 1  # user_email
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/profile/token_expiration")
            assert response.status_code == 200

        expiration = datetime.fromisoformat(response.json["expiration"]).replace(tzinfo=None)
        delta = abs(expiration - expiration_date)
        assert delta == timedelta(seconds=0)

    def test_no_token(self, app, client):
        user = users_factories.UserFactory(email=self.email)

        client = client.with_token(user.email)
        expected_num_queries = 1  # user
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/profile/token_expiration")
            assert response.status_code == 200
        assert response.json["expiration"] is None


class ResendEmailValidationTest:
    def test_resend_email_validation(self, client, app):
        user = users_factories.UserFactory(isEmailValidated=False)

        response = client.post("/native/v1/resend_email_validation", json={"email": user.email})

        assert response.status_code == 204
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(TransactionalEmail.EMAIL_CONFIRMATION.value)

    def test_for_already_validated_email_does_sent_passsword_reset(self, client, app):
        user = users_factories.UserFactory(isEmailValidated=True)

        response = client.post("/native/v1/resend_email_validation", json={"email": user.email})

        assert response.status_code == 204
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(TransactionalEmail.NEW_PASSWORD_REQUEST.value)

    def test_for_unknown_mail_does_nothing(self, client, app):
        response = client.post("/native/v1/resend_email_validation", json={"email": "aijfioern@mlks.com"})

        assert response.status_code == 204
        assert not mails_testing.outbox

    def test_for_deactivated_account_does_nothhing(self, client, app):
        user = users_factories.UserFactory(isEmailValidated=True, isActive=False)

        response = client.post("/native/v1/resend_email_validation", json={"email": user.email})

        assert response.status_code == 204
        assert not mails_testing.outbox

    def test_resend_validation_email_too_many_attempts(self, client):
        """
        Test that a user cannot request more than
        MAX_EMAIL_UPDATE_ATTEMPTS email update change within the last
        N days.
        """
        user = users_factories.UserFactory(isEmailValidated=False)

        response = client.post("/native/v1/resend_email_validation", json={"email": user.email})

        assert response.status_code == 204

        response = client.post("/native/v1/resend_email_validation", json={"email": user.email})

        assert response.status_code == 204

        response = client.post("/native/v1/resend_email_validation", json={"email": user.email})

        assert response.status_code == 204

        response = client.post("/native/v1/resend_email_validation", json={"email": user.email})

        assert response.status_code == 429
        assert response.json["code"] == "TOO_MANY_EMAIL_VALIDATION_RESENDS"
        assert response.json["message"] == "Le nombre de tentatives maximal est dépassé."


class EmailValidationRemainingResendsTest:
    def test_email_validation_remaining_resends(
        self,
        client,
    ):
        user = users_factories.UserFactory(isEmailValidated=False)

        response = client.get(f"/native/v1/email_validation_remaining_resends/{user.email}")
        assert response.status_code == 200

        assert response.json["remainingResends"] == 3
        client.post("/native/v1/resend_email_validation", json={"email": user.email})
        response = client.get(f"/native/v1/email_validation_remaining_resends/{user.email}")

        assert response.status_code == 200
        assert response.json["remainingResends"] == 2

    @time_machine.travel("2023-09-15 10:00", tick=False)
    def test_email_validation_counter_reset(
        self,
        client,
    ):
        user = users_factories.UserFactory(isEmailValidated=False)

        response = client.get(f"/native/v1/email_validation_remaining_resends/{user.email}")

        assert response.json["counterResetDatetime"] is None

        client.post("/native/v1/resend_email_validation", json={"email": user.email})
        response = client.get(f"/native/v1/email_validation_remaining_resends/{user.email}")

        assert response.json["counterResetDatetime"] == "2023-09-16T10:00:00Z"

    def test_email_validation_remaining_resends_with_unknown_email(
        self,
        client,
    ):

        expected_num_queries = 1  # user
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/email_validation_remaining_resends/test@example.com")

        assert response.json["remainingResends"] == 0
        assert response.json["counterResetDatetime"] is None


class ShowEligibleCardTest:
    @pytest.mark.parametrize("age,expected", [(17, False), (18, True), (19, False)])
    def test_against_different_age(self, age, expected):
        date_of_birth = datetime.utcnow() - relativedelta(years=age, days=5)
        date_of_creation = datetime.utcnow() - relativedelta(years=4)
        user = users_factories.UserFactory(dateOfBirth=date_of_birth, dateCreated=date_of_creation)
        assert account_serializers.UserProfileResponse.from_orm(user).show_eligible_card == expected

    @pytest.mark.parametrize("beneficiary,expected", [(False, True), (True, False)])
    def test_against_beneficiary(self, beneficiary, expected):
        date_of_birth = datetime.utcnow() - relativedelta(years=18, days=5)
        date_of_creation = datetime.utcnow() - relativedelta(years=4)
        roles = [users_models.UserRole.BENEFICIARY] if beneficiary else []
        user = users_factories.UserFactory(
            dateOfBirth=date_of_birth,
            dateCreated=date_of_creation,
            roles=roles,
        )
        assert account_serializers.UserProfileResponse.from_orm(user).show_eligible_card == expected

    def test_user_eligible_but_created_after_18(self):
        date_of_birth = datetime.utcnow() - relativedelta(years=18, days=5)
        date_of_creation = datetime.utcnow()
        user = users_factories.UserFactory(dateOfBirth=date_of_birth, dateCreated=date_of_creation)
        assert account_serializers.UserProfileResponse.from_orm(user).show_eligible_card is False


class SendPhoneValidationCodeTest:
    def test_send_phone_validation_code(self, client, app):
        user = users_factories.UserFactory()
        client.with_token(email=user.email)

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33601020304"})

        assert response.status_code == 204

        assert int(app.redis_client.get(f"sent_SMS_counter_user_{user.id}")) == 1

        encoded_token = app.redis_client.get(
            token_utils.SixDigitsToken.get_redis_key(token_utils.TokenType.PHONE_VALIDATION, user.id)
        )
        assert encoded_token is not None
        token = token_utils.SixDigitsToken.load_without_checking(
            encoded_token, token_utils.TokenType.PHONE_VALIDATION, user.id
        )
        assert token.get_expiration_date_from_token() >= datetime.utcnow() + timedelta(hours=10)
        assert token.get_expiration_date_from_token() < datetime.utcnow() + timedelta(hours=13)

        assert sms_testing.requests == [
            {"recipient": "+33601020304", "content": f"{token.encoded_token} est ton code de confirmation pass Culture"}
        ]
        assert len(token.encoded_token) == 6
        assert 0 <= int(token.encoded_token) < 1000000
        assert token.data["phone_number"] == "+33601020304"

        # validate phone number with generated code
        response = client.post("/native/v1/validate_phone_number", json={"code": token.encoded_token})

        assert response.status_code == 204
        user = users_models.User.query.get(user.id)
        assert user.is_phone_validated

    @override_settings(MAX_SMS_SENT_FOR_PHONE_VALIDATION=1)
    def test_send_phone_validation_code_too_many_attempts(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=18, days=5),
        )
        client.with_token(email=user.email)

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33601020304"})
        assert response.status_code == 204

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33601020304"})
        assert response.status_code == 400
        assert response.json["code"] == "TOO_MANY_SMS_SENT"

        # check that a fraud check has been created
        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            userId=user.id,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            thirdPartyId=f"PC-{user.id}",
            status=fraud_models.FraudCheckStatus.KO,
        ).one_or_none()

        assert fraud_check is not None
        assert fraud_check.eligibilityType == users_models.EligibilityType.AGE18

        content = fraud_check.resultContent
        expected_reason = "Le nombre maximum de sms envoyés est atteint"
        assert fraud_check.reasonCodes == [fraud_models.FraudReasonCode.SMS_SENDING_LIMIT_REACHED]
        assert fraud_check.reason == expected_reason
        assert content["phone_number"] == "+33601020304"

    def test_send_phone_validation_code_already_beneficiary(self, client):
        user = users_factories.BeneficiaryGrant18Factory()
        client.with_token(email=user.email)

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33601020304"})

        assert response.status_code == 400

        assert not token_utils.SixDigitsToken.token_exists(token_utils.TokenType.PHONE_VALIDATION, user.id)

    def test_send_phone_validation_code_for_new_phone_with_already_beneficiary(self, client, app):
        user = users_factories.BeneficiaryGrant18Factory(
            isEmailValidated=True, phoneNumber="+33601020304", roles=[users_models.UserRole.BENEFICIARY]
        )
        client.with_token(email=user.email)

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33102030405"})

        assert response.status_code == 400

        assert not token_utils.SixDigitsToken.token_exists(token_utils.TokenType.PHONE_VALIDATION, user.id)
        db.session.refresh(user)
        assert user.phoneNumber == "+33601020304"

    def test_send_phone_validation_code_for_new_phone_updates_phone(self, client):
        user = users_factories.UserFactory(isEmailValidated=True, phoneNumber="+33601020304")
        client.with_token(email=user.email)

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33102030405"})

        assert response.status_code == 204

        db.session.refresh(user)
        assert user.phoneNumber == "+33102030405"

    def test_send_phone_validation_code_for_new_unvalidated_duplicated_phone_number(self, client, app):
        users_factories.UserFactory(isEmailValidated=True, phoneNumber="+33102030405")
        user = users_factories.UserFactory(isEmailValidated=True, phoneNumber="+33601020304")
        client.with_token(email=user.email)

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33102030405"})

        assert response.status_code == 204

        db.session.refresh(user)
        assert user.phoneNumber == "+33102030405"

    def test_send_phone_validation_code_for_new_validated_duplicated_phone_number(self, client):
        orig_user = users_factories.UserFactory(
            isEmailValidated=True,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            phoneNumber="+33102030405",
            roles=[users_models.UserRole.BENEFICIARY],
        )
        user = users_factories.UserFactory(
            isEmailValidated=True,
            phoneNumber="+33601020304",
            dateOfBirth=datetime.utcnow() - relativedelta(years=18, days=5),
        )
        client.with_token(email=user.email)

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33102030405"})

        assert response.status_code == 400

        assert not token_utils.SixDigitsToken.token_exists(token_utils.TokenType.PHONE_VALIDATION, user.id)
        db.session.refresh(user)
        assert user.phoneNumber == "+33601020304"
        assert response.json == {
            "message": "Un compte est déjà associé à ce numéro. Renseigne un autre numéro ou connecte-toi au compte existant.",
            "code": "PHONE_ALREADY_EXISTS",
        }

        # check that a fraud check has been created
        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            userId=user.id,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            thirdPartyId=f"PC-{user.id}",
            status=fraud_models.FraudCheckStatus.KO,
        ).one_or_none()

        assert fraud_check is not None
        assert fraud_check.eligibilityType == users_models.EligibilityType.AGE18

        content = fraud_check.resultContent
        assert fraud_check.reasonCodes == [fraud_models.FraudReasonCode.PHONE_ALREADY_EXISTS]
        assert fraud_check.reason == f"Le numéro est déjà utilisé par l'utilisateur {orig_user.id}"
        assert content["phone_number"] == "+33102030405"

        assert (
            subscription_api.get_phone_validation_subscription_item(user, users_models.EligibilityType.AGE18).status
            == subscription_models.SubscriptionItemStatus.KO
        )

    def test_send_phone_validation_code_with_invalid_number(self, client):
        # user's phone number should be in international format (E.164): +33601020304
        user = users_factories.UserFactory(isEmailValidated=True)
        client.with_token(email=user.email)

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "060102030405"})

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_PHONE_NUMBER"
        assert not token_utils.SixDigitsToken.token_exists(token_utils.TokenType.PHONE_VALIDATION, user.id)

    def test_send_phone_validation_code_with_non_french_number(self, client):
        user = users_factories.UserFactory(isEmailValidated=True)
        client.with_token(email=user.email)

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+46766123456"})

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_COUNTRY_CODE"
        assert response.json["message"] == "L'indicatif téléphonique n'est pas accepté"
        assert not token_utils.SixDigitsToken.token_exists(token_utils.TokenType.PHONE_VALIDATION, user.id)

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(userId=user.id).one()
        assert fraud_check.reasonCodes == [fraud_models.FraudReasonCode.INVALID_PHONE_COUNTRY_CODE]
        assert fraud_check.type == fraud_models.FraudCheckType.PHONE_VALIDATION

    @override_settings(BLACKLISTED_SMS_RECIPIENTS={"+33601020304"})
    def test_blocked_phone_number(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=18, days=5),
        )
        client.with_token(email=user.email)

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33601020304"})

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_PHONE_NUMBER"

        assert not token_utils.SixDigitsToken.token_exists(token_utils.TokenType.PHONE_VALIDATION, user.id)
        db.session.refresh(user)
        assert user.phoneNumber is None

        # check that a fraud check has been created
        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            userId=user.id,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            thirdPartyId=f"PC-{user.id}",
            status=fraud_models.FraudCheckStatus.KO,
        ).one_or_none()

        assert fraud_check.eligibilityType == users_models.EligibilityType.AGE18

        content = fraud_check.resultContent
        assert fraud_check.reasonCodes == [fraud_models.FraudReasonCode.BLACKLISTED_PHONE_NUMBER]
        assert fraud_check.reason == "Le numéro saisi est interdit"
        assert content["phone_number"] == "+33601020304"


class ValidatePhoneNumberTest:
    mock_redis_client = fakeredis.FakeStrictRedis()

    def test_validate_phone_number(self, client, app):
        user = users_factories.UserFactory(
            phoneNumber="+33607080900", dateOfBirth=datetime.utcnow() - relativedelta(years=18)
        )
        client.with_token(email=user.email)
        token = create_phone_validation_token(user, "+33607080900")

        # try one attempt with wrong code
        client.post("/native/v1/validate_phone_number", {"code": "wrong code"})
        response = client.post("/native/v1/validate_phone_number", {"code": token.encoded_token})

        assert response.status_code == 204
        user = users_models.User.query.get(user.id)
        assert user.is_phone_validated
        assert not user.has_beneficiary_role

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            user=user, type=fraud_models.FraudCheckType.PHONE_VALIDATION
        ).one()
        assert fraud_check.status == fraud_models.FraudCheckStatus.OK
        assert fraud_check.eligibilityType == users_models.EligibilityType.AGE18

        assert not token_utils.SixDigitsToken.token_exists(token_utils.TokenType.PHONE_VALIDATION, user.id)

        assert int(app.redis_client.get(f"phone_validation_attempts_user_{user.id}")) == 2

    def test_can_not_validate_phone_number_with_first_sent_code(self, client, app):
        first_number = "+33611111111"
        second_number = "+33622222222"
        user = users_factories.UserFactory(phoneNumber=second_number)
        client.with_token(email=user.email)
        first_token = create_phone_validation_token(user, first_number)
        create_phone_validation_token(user, second_number)

        response = client.post("/native/v1/validate_phone_number", {"code": first_token.encoded_token})

        assert response.status_code == 400
        user = users_models.User.query.get(user.id)
        assert not user.is_phone_validated

        assert int(app.redis_client.get(f"phone_validation_attempts_user_{user.id}")) == 1

    def test_validate_phone_number_and_become_beneficiary(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=18, days=5),
            phoneNumber="+33607080900",
            activity="Lycéen",
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.OK
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.HONOR_STATEMENT, status=fraud_models.FraudCheckStatus.OK
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

        client.with_token(email=user.email)
        token = create_phone_validation_token(user, "+33607080900")

        response = client.post("/native/v1/validate_phone_number", {"code": token.encoded_token})

        assert response.status_code == 204
        user = users_models.User.query.get(user.id)
        assert user.is_phone_validated
        assert user.has_beneficiary_role

    @override_settings(MAX_PHONE_VALIDATION_ATTEMPTS=1)
    def test_validate_phone_number_too_many_attempts(self, client, app):
        user = users_factories.UserFactory(
            phoneNumber="+33607080900",
            dateOfBirth=datetime.utcnow() - relativedelta(years=18, days=5),
        )
        client.with_token(email=user.email)
        token = create_phone_validation_token(user, "+33607080900")

        response = client.post("/native/v1/validate_phone_number", {"code": "wrong code"})
        response = client.post("/native/v1/validate_phone_number", {"code": token.encoded_token})

        assert response.status_code == 400
        assert response.json["message"] == "Le nombre de tentatives maximal est dépassé"
        assert response.json["code"] == "TOO_MANY_VALIDATION_ATTEMPTS"

        db.session.refresh(user)
        assert not user.is_phone_validated

        attempts_count = int(app.redis_client.get(f"phone_validation_attempts_user_{user.id}"))
        assert attempts_count == 1

        fraud_checks = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            userId=user.id,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            thirdPartyId=f"PC-{user.id}",
        ).all()
        for fraud_check in fraud_checks:
            assert fraud_check.eligibilityType == users_models.EligibilityType.AGE18

            expected_reason = f"Le nombre maximum de tentatives de validation est atteint: {attempts_count}"
            content = fraud_check.resultContent
            assert fraud_check.reasonCodes == [fraud_models.FraudReasonCode.PHONE_VALIDATION_ATTEMPTS_LIMIT_REACHED]

            assert fraud_check.reason == expected_reason
            assert content["phone_number"] == "+33607080900"

    @override_settings(MAX_SMS_SENT_FOR_PHONE_VALIDATION=1)
    @time_machine.travel("2022-05-17 15:00")
    def test_phone_validation_remaining_attempts(self, client):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18, days=5))
        client.with_token(email=user.email)
        response = client.get("/native/v1/phone_validation/remaining_attempts")

        assert response.json["counterResetDatetime"] is None
        assert response.json["remainingAttempts"] == 1

        client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33607080900"})

        response = client.get("/native/v1/phone_validation/remaining_attempts")
        # the test can take more than a second to run, so we need to check the date against an interval
        assert "2022-05-18T02:50:00Z" <= response.json["counterResetDatetime"] <= "2022-05-18T03:00:00Z"
        assert response.json["remainingAttempts"] == 0

    def test_wrong_code(self, client):
        user = users_factories.UserFactory(phoneNumber="+33607080900")
        client.with_token(email=user.email)
        create_phone_validation_token(user, "+33607080900")

        response = client.post("/native/v1/validate_phone_number", {"code": "mauvais-code"})

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_VALIDATION_CODE"
        assert (
            response.json["message"]
            == "Le code est invalide. Saisis le dernier code reçu par SMS. Il te reste 2 tentatives."
        )
        response = client.post("/native/v1/validate_phone_number", {"code": "mauvais-code"})
        assert response.status_code == 400
        assert response.json["code"] == "INVALID_VALIDATION_CODE"
        assert (
            response.json["message"]
            == "Le code est invalide. Saisis le dernier code reçu par SMS. Il te reste 1 tentative."
        )
        assert fraud_models.BeneficiaryFraudCheck.query.filter_by(userId=user.id).first() is None

        response = client.post("/native/v1/validate_phone_number", {"code": "mauvais-code"})
        assert response.status_code == 400
        assert response.json["code"] == "TOO_MANY_VALIDATION_ATTEMPTS"
        assert response.json["message"] == "Le nombre de tentatives maximal est dépassé"

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(userId=user.id).one()
        assert fraud_check.type == fraud_models.FraudCheckType.PHONE_VALIDATION
        assert fraud_check.reasonCodes == [fraud_models.FraudReasonCode.PHONE_VALIDATION_ATTEMPTS_LIMIT_REACHED]

        assert not users_models.User.query.get(user.id).is_phone_validated
        assert token_utils.SixDigitsToken.token_exists(token_utils.TokenType.PHONE_VALIDATION, user.id)

    def test_expired_code(self, client):
        with mock.patch("flask.current_app.redis_client", self.mock_redis_client):
            user = users_factories.UserFactory(phoneNumber="+33607080900")
            token = create_phone_validation_token(user, "+33607080900")

            with time_machine.travel(datetime.utcnow() + timedelta(hours=15)):
                client.with_token(email=user.email)
                response = client.post("/native/v1/validate_phone_number", {"code": token.encoded_token})

            assert response.status_code == 400
            assert response.json["code"] == "INVALID_VALIDATION_CODE"

            assert not users_models.User.query.get(user.id).is_phone_validated
            assert token_utils.SixDigitsToken.token_exists(token_utils.TokenType.PHONE_VALIDATION, user.id)

    def test_validate_phone_number_with_already_validated_phone(self, client):
        users_factories.UserFactory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            phoneNumber="+33607080900",
            roles=[users_models.UserRole.BENEFICIARY],
        )
        user = users_factories.UserFactory(phoneNumber="+33607080900")
        client.with_token(email=user.email)
        token = create_phone_validation_token(user, "+33607080900")

        # try one attempt with wrong code
        response = client.post("/native/v1/validate_phone_number", {"code": token.encoded_token})

        assert response.status_code == 400
        user = users_models.User.query.get(user.id)
        assert not user.is_phone_validated


class SuspendAccountTest:
    def test_suspend_account(self, client, app):
        booking = booking_factories.BookingFactory()
        user = booking.user

        client.with_token(email=user.email)
        response = client.post("/native/v1/account/suspend")

        assert response.status_code == 204
        assert booking.status == BookingStatus.CANCELLED
        db.session.refresh(user)
        assert not user.isActive
        assert user.suspension_reason == users_constants.SuspensionReason.UPON_USER_REQUEST
        assert user.suspension_date
        assert len(user.suspension_action_history) == 1
        assert user.suspension_action_history[0].userId == user.id
        assert user.suspension_action_history[0].authorUserId == user.id

    def test_suspend_suspended_account(self, client, app):
        # Ensure that a beneficiary user can't change the reason for being suspended
        user = users_factories.BeneficiaryGrant18Factory(isActive=False)
        reason = users_constants.SuspensionReason.FRAUD_SUSPICION
        history_factories.SuspendedUserActionHistoryFactory(user=user, reason=reason)

        client.with_token(email=user.email)
        response = client.post("/native/v1/account/suspend")

        # Any API call is forbidden for suspended user
        assert response.status_code == 403
        db.session.refresh(user)
        assert not user.isActive
        assert user.suspension_reason == reason
        assert len(user.suspension_action_history) == 1


def build_user_at_id_check(age):
    user = users_factories.UserFactory(
        dateOfBirth=datetime.utcnow() - relativedelta(years=age, days=5),
        phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
    )
    fraud_factories.ProfileCompletionFraudCheckFactory(
        user=user,
        eligibilityType=users_models.EligibilityType.AGE18,
        resultContent=fraud_factories.ProfileCompletionContentFactory(first_name="Sally", last_name="Mara"),
    )
    return user


class IdentificationSessionTest:
    def test_request(self, client, ubble_mock):
        user = build_user_at_id_check(18)

        client.with_token(user.email)

        response = client.post("/native/v1/ubble_identification", json={"redirectUrl": "http://example.com/deeplink"})

        assert response.status_code == 200
        assert len(user.beneficiaryFraudChecks) == 2
        assert ubble_mock.call_count == 1

        assert ubble_mock.request_history[0].json() == {
            "data": {
                "type": "identifications",
                "attributes": {
                    "identification-form": {"external-user-id": user.id, "phone-number": None},
                    "reference-data": {"first-name": "Sally", "last-name": "Mara"},
                    "webhook": "http://localhost/webhooks/ubble/application_status",
                    "redirect_url": "http://example.com/deeplink",
                },
            }
        }

        check = next(check for check in user.beneficiaryFraudChecks if check.type == fraud_models.FraudCheckType.UBBLE)
        assert check.type == fraud_models.FraudCheckType.UBBLE
        assert check.status == fraud_models.FraudCheckStatus.STARTED
        assert response.json["identificationUrl"] == "https://id.ubble.ai/29d9eca4-dce6-49ed-b1b5-8bb0179493a8"

    @pytest.mark.parametrize("age", [14, 19, 20])
    def test_request_not_eligible(self, client, ubble_mock, age):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=age, days=5))

        client.with_token(user.email)

        response = client.post("/native/v1/ubble_identification", json={"redirectUrl": "http://example.com/deeplink"})

        assert response.status_code == 400
        assert response.json["code"] == "IDCHECK_NOT_ELIGIBLE"
        assert len(user.beneficiaryFraudChecks) == 0
        assert ubble_mock.call_count == 0

    def test_request_connection_error(self, client, ubble_mock_connection_error):
        user = build_user_at_id_check(18)

        client.with_token(user.email)

        response = client.post("/native/v1/ubble_identification", json={"redirectUrl": "http://example.com/deeplink"})

        assert response.status_code == 503
        assert response.json["code"] == "IDCHECK_SERVICE_UNAVAILABLE"
        assert (
            fraud_models.BeneficiaryFraudCheck.query.filter_by(
                user=user, type=fraud_models.FraudCheckType.UBBLE
            ).count()
            == 0
        )
        assert ubble_mock_connection_error.call_count == 1

    def test_request_ubble_http_error_status(self, client, ubble_mock_http_error_status):
        user = build_user_at_id_check(18)

        client.with_token(user.email)

        response = client.post("/native/v1/ubble_identification", json={"redirectUrl": "http://example.com/deeplink"})

        assert response.status_code == 500
        assert response.json["code"] == "IDCHECK_SERVICE_ERROR"
        assert (
            fraud_models.BeneficiaryFraudCheck.query.filter_by(
                user=user, type=fraud_models.FraudCheckType.UBBLE
            ).count()
            == 0
        )
        assert ubble_mock_http_error_status.call_count == 1

    @pytest.mark.parametrize(
        "fraud_check_status,ubble_status",
        [
            (fraud_models.FraudCheckStatus.PENDING, ubble_fraud_models.UbbleIdentificationStatus.PROCESSING),
            (fraud_models.FraudCheckStatus.OK, ubble_fraud_models.UbbleIdentificationStatus.PROCESSED),
            (fraud_models.FraudCheckStatus.KO, ubble_fraud_models.UbbleIdentificationStatus.PROCESSED),
        ],
    )
    def test_request_ubble_second_check_blocked(self, client, fraud_check_status, ubble_status):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18, days=5))
        client.with_token(user.email)

        # Perform phone validation
        user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED

        # Perform first id check with Ubble
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_check_status,
            resultContent=fraud_factories.UbbleContentFactory(status=ubble_status),
        )

        # Initiate second id check with Ubble
        # It should be blocked - only one identification is allowed
        response = client.post("/native/v1/ubble_identification", json={"redirectUrl": "http://example.com/deeplink"})

        assert response.status_code == 400
        assert response.json["code"] == "IDCHECK_ALREADY_PROCESSED"
        assert len(user.beneficiaryFraudChecks) == 1

    def test_request_ubble_second_check_after_first_aborted(self, client, ubble_mock):
        user = build_user_at_id_check(18)
        client.with_token(user.email)

        # Perform first id check with Ubble
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.CANCELED,
            resultContent=fraud_factories.UbbleContentFactory(
                status=ubble_fraud_models.UbbleIdentificationStatus.ABORTED
            ),
        )

        # Initiate second id check with Ubble
        # Accepted because the first one was canceled
        response = client.post("/native/v1/ubble_identification", json={"redirectUrl": "http://example.com/deeplink"})

        assert response.status_code == 200
        assert len(user.beneficiaryFraudChecks) == 3
        assert ubble_mock.call_count == 1

        sorted_fraud_checks = sorted(user.beneficiaryFraudChecks, key=lambda x: x.id)
        check = sorted_fraud_checks[-1]
        assert check.type == fraud_models.FraudCheckType.UBBLE
        assert response.json["identificationUrl"] == "https://id.ubble.ai/29d9eca4-dce6-49ed-b1b5-8bb0179493a8"

    @pytest.mark.parametrize(
        "retry_number,expected_status",
        [(1, 200), (2, 200), (3, 400), (4, 400)],
    )
    @pytest.mark.parametrize(
        "reason",
        [
            fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED,
            fraud_models.FraudReasonCode.ID_CHECK_EXPIRED,
            fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE,
        ],
    )
    def test_request_ubble_retry(self, client, ubble_mock, reason, retry_number, expected_status):
        user = build_user_at_id_check(18)
        client.with_token(user.email)

        # Perform previous Ubble identifications
        for _ in range(0, retry_number):
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.UBBLE,
                status=fraud_models.FraudCheckStatus.SUSPICIOUS,
                reasonCodes=[reason],
                resultContent=fraud_factories.UbbleContentFactory(
                    status=ubble_fraud_models.UbbleIdentificationStatus.PROCESSED
                ),
            )

        len_fraud_checks_before = len(user.beneficiaryFraudChecks)

        response = client.post("/native/v1/ubble_identification", json={"redirectUrl": "http://example.com/deeplink"})

        assert response.status_code == expected_status

        if response.status_code == 200:
            assert len(user.beneficiaryFraudChecks) == len_fraud_checks_before + 1

        if response.status_code == 400:
            assert len(user.beneficiaryFraudChecks) == len_fraud_checks_before

    @pytest.mark.parametrize(
        "reason",
        [
            fraud_models.FraudReasonCode.DUPLICATE_USER,
            fraud_models.FraudReasonCode.ID_CHECK_DATA_MATCH,
        ],
    )
    def test_request_ubble_retry_not_allowed(self, client, ubble_mock, reason):
        user = build_user_at_id_check(18)
        client.with_token(user.email)

        # Perform previous Ubble identification
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[reason],
            resultContent=fraud_factories.UbbleContentFactory(
                status=ubble_fraud_models.UbbleIdentificationStatus.PROCESSED
            ),
        )

        response = client.post("/native/v1/ubble_identification", json={"redirectUrl": "http://example.com/deeplink"})

        assert response.status_code == 400
        assert len(user.beneficiaryFraudChecks) == 2  # 2 previous ubble checks

    def test_allow_rerun_identification_from_started(self, client, ubble_mock):
        user = build_user_at_id_check(18)
        client.with_token(user.email)

        expected_url = "https://id.ubble.ai/ef055567-3794-4ca5-afad-dce60fe0f227"

        ubble_content = fraud_factories.UbbleContentFactory(
            status=ubble_fraud_models.UbbleIdentificationStatus.INITIATED,
            identification_url=expected_url,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.STARTED,
            user=user,
            resultContent=ubble_content,
        )
        response = client.post("/native/v1/ubble_identification", json={"redirectUrl": "http://example.com/deeplink"})

        assert response.status_code == 200
        assert len(user.beneficiaryFraudChecks) == 2  # profile, ubble
        assert ubble_mock.call_count == 0

        check = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_models.FraudCheckType.UBBLE
        ][0]
        assert check
        assert response.json["identificationUrl"] == expected_url


class AccountSecurityTest:
    def test_account_hacker_changes_password(self, client, app):
        """
        This scenario has been suggested by a security bug hunter: it is possible for a hacker to register with the
        email someone else registered earlier, before the hacked user clicks on email confirmation link. The hacker can
        change user's password this way.
        """
        assert users_models.User.query.first() is None
        data = {
            "appsFlyerPlatform": "web",
            "birthdate": "2004-01-01",
            "email": "patrick@example.com",
            "marketingEmailSubscription": True,
            "password": "User@AZERTY1234",
            "postalCode": "",
            "token": "usertoken",
        }

        response = client.post("/native/v1/account", json=data)
        assert response.status_code == 204, response.json

        user = users_models.User.query.first()
        assert user is not None
        assert user.email == data["email"]
        assert user.isEmailValidated is False

        user_password = user.password

        hacker_data = data.copy()
        hacker_data.update(
            {
                "password": "Hacker@AZERTY5678",
                "token": "hackertoken",
            }
        )

        hacker_response = client.post("/native/v1/account", json=hacker_data)
        assert hacker_response.status_code == 204, hacker_response.json

        assert users_models.User.query.count() == 1
        user = users_models.User.query.first()
        assert user.password == user_password


class GetAccountSuspendedDateTest:
    @time_machine.travel("2020-10-15 00:00:00", tick=False)
    def test_suspended_account(self, client):
        """
        Test that a call for a suspended account returns its suspension
        date
        """
        user = users_factories.BeneficiaryGrant18Factory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )

        client.with_token(email=user.email)
        expected_num_queries = 2  # user + action_history
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/account/suspension_date")
            assert response.status_code == 200

        assert response.json["date"] == "2020-10-14T00:00:00Z"

    class ShouldNotRespondWithSuspensionDateTest:
        def test_unsuspended_account(self, client):
            """
            Test that a call for a unsuspended account returns no date
            """
            user = users_factories.BeneficiaryGrant18Factory(isActive=False)
            history_factories.SuspendedUserActionHistoryFactory(
                user=user, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
            )
            history_factories.UnsuspendedUserActionHistoryFactory(user=user)

            self.assert_no_suspension_date_returned(client, user)

        def test_never_suspended_account(self, client):
            """
            Test that a call for an account that has never been suspended
            returns no date
            """
            user = users_factories.BeneficiaryGrant18Factory(isActive=True)
            self.assert_no_suspension_date_returned(client, user)

        def test_suspended_fraud_suspicion(self, client):
            """
            Test that a call for an account that has been suspended because
            of fraud suspicion returns no date
            """
            user = users_factories.BeneficiaryGrant18Factory(isActive=False)
            history_factories.SuspendedUserActionHistoryFactory(
                user=user, reason=users_constants.SuspensionReason.FRAUD_SUSPICION
            )

            self.assert_no_suspension_date_returned(client, user)

        def assert_no_suspension_date_returned(self, client, user) -> None:
            client.with_token(email=user.email)

            expected_num_queries = 2  # user + action_history
            with assert_num_queries(expected_num_queries):
                response = client.get("/native/v1/account/suspension_date")
                assert response.status_code == 403


class SuspensionStatusTest:
    def test_fraud_suspicion_account_status(self, client):
        user = users_factories.BeneficiaryGrant18Factory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, reason=users_constants.SuspensionReason.FRAUD_SUSPICION
        )

        self.assert_status(client, user, "SUSPENDED")

    def test_suspended_upon_user_request_status(self, client):
        user = users_factories.BeneficiaryGrant18Factory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )

        self.assert_status(client, user, "SUSPENDED_UPON_USER_REQUEST")

    def test_suspicious_login_reported_by_user_request_status(self, client):
        user = users_factories.BeneficiaryGrant18Factory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, reason=users_constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER
        )

        self.assert_status(client, user, "SUSPICIOUS_LOGIN_REPORTED_BY_USER")

    def test_deleted_account_status(self, client):
        user = users_factories.BeneficiaryGrant18Factory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(user=user, reason=users_constants.SuspensionReason.DELETED)

        self.assert_status(client, user, "DELETED")

    def test_active_account(self, client):
        user = users_factories.BeneficiaryGrant18Factory(isActive=True)
        self.assert_status(client, user, "ACTIVE")

    def assert_status(self, client, user, status):
        client.with_token(email=user.email)
        response = client.get("/native/v1/account/suspension_status")

        assert response.status_code == 200
        assert response.json["status"] == status


class UnsuspendAccountTest:
    def test_suspended_upon_user_request(self, client):
        user = users_factories.BeneficiaryGrant18Factory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )

        client.with_token(email=user.email)
        response = client.post("/native/v1/account/unsuspend")

        assert response.status_code == 204

        db.session.refresh(user)
        assert user.isActive

        assert len(mails_testing.outbox) == 1

        mail = mails_testing.outbox[0]
        assert mail["template"] == dataclasses.asdict(TransactionalEmail.ACCOUNT_UNSUSPENDED.value)
        assert mail["To"] == user.email

    def test_error_when_not_suspended(self, client):
        user = users_factories.BeneficiaryGrant18Factory(isActive=True)

        response = client.with_token(email=user.email).post("/native/v1/account/unsuspend")
        self.assert_code(response, "ALREADY_UNSUSPENDED")

    @pytest.mark.parametrize(
        "suspension_reason",
        [
            users_constants.SuspensionReason.FRAUD_SUSPICION,
            users_constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER,
        ],
    )
    def test_error_when_not_suspended_upon_user_request(self, client, suspension_reason):
        user = users_factories.BeneficiaryGrant18Factory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(user=user, reason=suspension_reason)

        response = client.with_token(email=user.email).post("/native/v1/account/unsuspend")
        self.assert_code_and_not_active(response, user, "UNSUSPENSION_NOT_ALLOWED")

    def test_error_when_suspension_time_limit_reached(self, client):
        user = users_factories.BeneficiaryGrant18Factory(isActive=False)

        suspension_date = date.today() - timedelta(days=users_constants.ACCOUNT_UNSUSPENSION_DELAY + 1)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, actionDate=suspension_date, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )

        response = client.with_token(email=user.email).post("/native/v1/account/unsuspend")
        self.assert_code_and_not_active(response, user, "UNSUSPENSION_LIMIT_REACHED")

    def assert_code(self, response, code):
        assert response.status_code == 403
        assert response.json["code"] == code

    def assert_code_and_not_active(self, response, user, code):
        self.assert_code(response, code)

        db.session.refresh(user)
        assert not user.isActive


class SuspendAccountForSuspiciousLoginTest:
    def test_error_when_token_is_invalid(self, client):
        response = client.post("/native/v1/account/suspend_for_suspicious_login", {"token": "abc"})

        assert response.status_code == 400
        assert response.json["reason"] == "Le token est invalide."

    def test_error_when_token_has_invalid_signature(self, client):
        token = jwt.encode(
            {"userId": 1},
            "wrong_jwt_secret_key",
            algorithm=ALGORITHM_HS_256,
        )
        response = client.post("/native/v1/account/suspend_for_suspicious_login", {"token": token})

        assert response.status_code == 400
        assert response.json["reason"] == "Le token est invalide."

    def test_error_when_token_is_expired(self, client):
        with patch("flask.current_app.redis_client", fakeredis.FakeStrictRedis()):
            current_time = datetime.utcnow()
            passed_expiration_date = (
                current_time - users_constants.SUSPICIOUS_LOGIN_EMAIL_TOKEN_LIFE_TIME - timedelta(days=1)
            )
            with time_machine.travel(passed_expiration_date):
                user = users_factories.BaseUserFactory()
                token = token_utils.Token.create(
                    token_utils.TokenType.SUSPENSION_SUSPICIOUS_LOGIN,
                    ttl=users_constants.SUSPICIOUS_LOGIN_EMAIL_TOKEN_LIFE_TIME,
                    user_id=user.id,
                )
            with time_machine.travel(current_time):
                response = client.post(
                    "/native/v1/account/suspend_for_suspicious_login", {"token": token.encoded_token}
                )

                assert response.status_code == 401
                assert response.json["reason"] == "Le token a expiré."

    def test_error_when_account_suspension_attempt_with_unknown_user(self, client):
        token = token_utils.Token.create(
            token_utils.TokenType.SUSPENSION_SUSPICIOUS_LOGIN,
            ttl=users_constants.SUSPICIOUS_LOGIN_EMAIL_TOKEN_LIFE_TIME,
            user_id=1,
        )

        response = client.post("/native/v1/account/suspend_for_suspicious_login", {"token": token.encoded_token})

        assert response.status_code == 404

    def test_suspend_account_for_suspicious_login(self, client):
        booking = booking_factories.BookingFactory()
        user = booking.user
        token = token_utils.Token.create(
            token_utils.TokenType.SUSPENSION_SUSPICIOUS_LOGIN,
            ttl=users_constants.SUSPICIOUS_LOGIN_EMAIL_TOKEN_LIFE_TIME,
            user_id=user.id,
        )

        response = client.post("/native/v1/account/suspend_for_suspicious_login", {"token": token.encoded_token})

        assert response.status_code == 204
        assert booking.status == BookingStatus.CANCELLED
        db.session.refresh(user)
        assert not user.isActive
        assert user.suspension_reason == users_constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER
        assert user.suspension_date
        assert len(user.suspension_action_history) == 1
        assert user.suspension_action_history[0].userId == user.id
        assert user.suspension_action_history[0].authorUserId == user.id
