import dataclasses
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
import logging
import re
from unittest.mock import patch
from urllib.parse import parse_qs
from urllib.parse import urlparse
import uuid

from dateutil.relativedelta import relativedelta
from freezegun.api import freeze_time
import jwt
import pytest

from pcapi import settings
from pcapi.core.bookings import factories as booking_factories
from pcapi.core.bookings.factories import CancelledIndividualBookingFactory
from pcapi.core.bookings.factories import IndividualBookingFactory
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.ubble import models as ubble_fraud_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.subscription.api as subscription_api
import pcapi.core.subscription.factories as subscription_factories
import pcapi.core.subscription.messages as subscription_messages
import pcapi.core.subscription.models as subscription_models
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users import testing as users_testing
from pcapi.core.users.api import create_phone_validation_token
from pcapi.core.users.constants import SuspensionReason
from pcapi.core.users.email import update as email_update
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import PhoneValidationStatusType
from pcapi.core.users.models import Token
from pcapi.core.users.models import TokenType
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole
from pcapi.core.users.models import VOID_PUBLIC_NAME
from pcapi.core.users.utils import ALGORITHM_HS_256
from pcapi.models import db
from pcapi.notifications.push import testing as push_testing
from pcapi.notifications.sms import testing as sms_testing
from pcapi.routes.native.v1.serialization import account as account_serializers
from pcapi.scripts.payment.user_recredit import recredit_underage_users

from tests.connectors import user_profiling_fixtures

from .utils import create_user_and_test_client


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
        response = client.get("/native/v1/me")

        assert response.status_code == 403
        assert response.json["email"] == ["Utilisateur introuvable"]

    def test_get_user_profile_not_active(self, client, app):
        users_factories.UserFactory(email=self.identifier, isActive=False)

        client.with_token(email=self.identifier)
        response = client.get("/native/v1/me")

        assert response.status_code == 403
        assert response.json["email"] == ["Utilisateur introuvable"]

    @freeze_time("2018-06-01")
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
            deposit__version=1,
            # The expiration date is taken in account in
            # `get_wallet_balance` and compared against the SQL
            # `now()` function, which is NOT overriden by
            # `freeze_time()`.
            deposit__expirationDate=datetime(2040, 1, 1),
            notificationSubscriptions={"marketing_push": True},
            publicName="jdo",
            **USER_DATA,
        )
        subscription_factories.SubscriptionMessageFactory(user=user)
        subscription_message = subscription_factories.SubscriptionMessageFactory(
            user=user, dateCreated=datetime.utcnow()
        )
        booking = IndividualBookingFactory(individualBooking__user=user, amount=Decimal("123.45"))
        CancelledIndividualBookingFactory(individualBooking__user=user, amount=Decimal("123.45"))

        client.with_token(self.identifier)

        response = client.get("/native/v1/me")

        EXPECTED_DATA = {
            "id": user.id,
            "bookedOffers": {str(booking.stock.offer.id): booking.id},
            "domainsCredit": {
                "all": {"initial": 50000, "remaining": 37655},
                "digital": {"initial": 20000, "remaining": 20000},
                "physical": {"initial": 20000, "remaining": 7655},
            },
            "dateOfBirth": "2000-01-01",
            "depositVersion": 1,
            "depositType": "GRANT_18",
            "depositExpirationDate": "2040-01-01T00:00:00Z",
            "eligibility": "age-18",
            "eligibilityEndDatetime": "2019-01-01T11:00:00Z",
            "eligibilityStartDatetime": "2015-01-01T00:00:00Z",
            "isBeneficiary": True,
            "isEligibleForBeneficiaryUpgrade": False,
            "roles": ["BENEFICIARY"],
            "pseudo": "jdo",
            "recreditAmountToShow": None,
            "showEligibleCard": False,
            "subscriptions": {"marketingPush": True, "marketingEmail": True},
            "subscriptionMessage": {
                "userMessage": subscription_message.userMessage,
                "popOverIcon": subscription_message.popOverIcon.value,
                "updatedAt": "2018-06-01T00:00:00Z",
                "callToAction": {
                    "callToActionTitle": subscription_message.callToActionTitle,
                    "callToActionLink": subscription_message.callToActionLink,
                    "callToActionIcon": subscription_message.callToActionIcon.value,
                },
            },
        }
        EXPECTED_DATA.update(USER_DATA)

        assert response.status_code == 200
        assert response.json == EXPECTED_DATA

    def test_get_user_not_beneficiary(self, client, app):
        users_factories.UserFactory(email=self.identifier)

        client.with_token(email=self.identifier)
        response = client.get("/native/v1/me")

        assert response.status_code == 200
        assert not response.json["domainsCredit"]

    def test_get_user_profile_empty_first_name(self, client, app):
        users_factories.UserFactory(email=self.identifier, firstName="", publicName=VOID_PUBLIC_NAME)

        client.with_token(email=self.identifier)
        response = client.get("/native/v1/me")

        assert response.status_code == 200
        assert response.json["email"] == self.identifier
        assert response.json["firstName"] is None
        assert response.json["pseudo"] is None
        assert not response.json["isBeneficiary"]
        assert response.json["roles"] == []

    def test_get_user_profile_recredit_amount_to_show(self, client, app):
        with freeze_time("2020-01-01"):
            users_factories.UnderageBeneficiaryFactory(email=self.identifier)

        with freeze_time("2021-01-02"):
            recredit_underage_users()

        client.with_token(email=self.identifier)
        me_response = client.get("/native/v1/me")
        assert me_response.json["recreditAmountToShow"] == 3000

    def test_user_messages_passes_pydantic_serialization(self, client):
        user = users_factories.UserFactory()
        client.with_token(user.email)

        subscription_messages.on_fraud_review_ko(user)
        response = client.get("/native/v1/me")
        assert response.status_code == 200

        subscription_messages.on_redirect_to_dms_from_idcheck(user)
        response = client.get("/native/v1/me")
        assert response.status_code == 200

        subscription_messages.on_idcheck_invalid_document_date(user)
        response = client.get("/native/v1/me")
        assert response.status_code == 200

        subscription_messages.on_idcheck_unread_document(user)
        response = client.get("/native/v1/me")
        assert response.status_code == 200

        subscription_messages.on_dms_application_received(user)
        response = client.get("/native/v1/me")
        assert response.status_code == 200

        subscription_messages.on_dms_application_refused(user)
        response = client.get("/native/v1/me")
        assert response.status_code == 200

        subscription_messages.on_duplicate_user(user)
        response = client.get("/native/v1/me")
        assert response.status_code == 200

    @override_features(ALLOW_IDCHECK_REGISTRATION=False)
    def test_maintenance_message(self, client):
        """
        Test that when a user has no subscription message and when the
        whole beneficiary signup process has been deactivated, the call
        to /me returns a generic maintenance message.
        """
        user = users_factories.UserFactory(
            email=self.identifier, dateOfBirth=datetime.utcnow() - relativedelta(years=18, days=5)
        )
        client.with_token(user.email)

        response = client.get("/native/v1/me")
        assert response.status_code == 200

        msg = response.json["subscriptionMessage"]
        assert msg["userMessage"] is not None
        assert msg["callToAction"] is None
        assert msg["popOverIcon"] == subscription_models.PopOverIcon.CLOCK.value

    @pytest.mark.parametrize(
        "feature_flags,roles,needsToFillCulturalSurvey",
        [
            (
                {"ENABLE_CULTURAL_SURVEY": True, "ENABLE_NATIVE_CULTURAL_SURVEY": True},
                [],
                True,
            ),
            (
                {"ENABLE_CULTURAL_SURVEY": True, "ENABLE_NATIVE_CULTURAL_SURVEY": False},
                [],
                False,
            ),
            (
                {"ENABLE_CULTURAL_SURVEY": True, "ENABLE_NATIVE_CULTURAL_SURVEY": False},
                [UserRole.BENEFICIARY],
                True,
            ),
            (
                {"ENABLE_CULTURAL_SURVEY": False, "ENABLE_NATIVE_CULTURAL_SURVEY": True},
                [],
                True,
            ),
            (
                {"ENABLE_CULTURAL_SURVEY": False, "ENABLE_NATIVE_CULTURAL_SURVEY": True},
                [UserRole.BENEFICIARY],
                True,
            ),
            (
                {"ENABLE_CULTURAL_SURVEY": False, "ENABLE_NATIVE_CULTURAL_SURVEY": False},
                [],
                False,
            ),
            (
                {"ENABLE_CULTURAL_SURVEY": False, "ENABLE_NATIVE_CULTURAL_SURVEY": False},
                [UserRole.BENEFICIARY],
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


class AccountCreationTest:
    identifier = "email@example.com"

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_account_creation(self, mocked_check_recaptcha_token_is_valid, client, app):
        assert User.query.first() is None
        data = {
            "email": "John.doe@example.com",
            "password": "Aazflrifaoi6@",
            "birthdate": "1960-12-31",
            "notifications": True,
            "token": "gnagna",
            "marketingEmailSubscription": True,
        }

        response = client.post("/native/v1/account", json=data)
        assert response.status_code == 204, response.json

        user = User.query.first()
        assert user is not None
        assert user.email == "john.doe@example.com"
        assert user.get_notification_subscriptions().marketing_email
        assert user.isEmailValidated is False
        mocked_check_recaptcha_token_is_valid.assert_called()
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.EMAIL_CONFIRMATION.value
        )
        assert len(push_testing.requests) == 2
        assert len(users_testing.sendinblue_requests) == 1

        email_validation_token = Token.query.filter_by(user=user, type=TokenType.EMAIL_VALIDATION).one_or_none()
        assert email_validation_token is not None
        assert "performance-tests" not in email_validation_token.value

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_account_creation_with_existing_validated_email_sends_email(
        self, mocked_check_recaptcha_token_is_valid, client, app
    ):
        users_factories.UserFactory(email=self.identifier)
        mocked_check_recaptcha_token_is_valid.return_value = None

        data = {
            "email": "eMail@example.com",
            "password": "Aazflrifaoi6@",
            "birthdate": "1960-12-31",
            "notifications": True,
            "token": "gnagna",
            "marketingEmailSubscription": True,
        }

        response = client.post("/native/v1/account", json=data)
        assert response.status_code == 204, response.json
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.EMAIL_ALREADY_EXISTS.value
        )
        assert not push_testing.requests

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_account_creation_with_unvalidated_existing_email_sends_email(
        self, mocked_check_recaptcha_token_is_valid, client, app
    ):
        subscriber = users_factories.UserFactory(email=self.identifier, isEmailValidated=False)
        users_factories.EmailValidationToken(user=subscriber)
        mocked_check_recaptcha_token_is_valid.return_value = None

        data = {
            "email": "eMail@example.com",
            "password": "Aazflrifaoi6@",
            "birthdate": "1960-12-31",
            "notifications": True,
            "token": "some-token",
            "marketingEmailSubscription": True,
        }

        response = client.post("/native/v1/account", json=data)
        assert response.status_code == 204, response.json
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.EMAIL_ALREADY_EXISTS.value
        )
        assert not push_testing.requests
        subscriber.checkPassword(data["password"])

        tokens = Token.query.all()
        assert len(tokens) == 2

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_too_young_account_creation(self, mocked_check_recaptcha_token_is_valid, client, app):
        assert User.query.first() is None
        data = {
            "email": "John.doe@example.com",
            "password": "Aazflrifaoi6@",
            "birthdate": (datetime.utcnow() - relativedelta(years=15)).date(),
            "notifications": True,
            "token": "gnagna",
            "marketingEmailSubscription": True,
        }

        response = client.post("/native/v1/account", json=data)
        assert response.status_code == 400
        assert not push_testing.requests

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    @override_settings(IS_PERFORMANCE_TESTS=True)
    def test_account_creation_performance_tests(self, mocked_check_recaptcha_token_is_valid, client):
        assert User.query.first() is None
        data = {
            "email": "John.doe@example.com",
            "password": "Aazflrifaoi6@",
            "birthdate": "1960-12-31",
            "firstName": "John",
            "lastName": "Doe",
            "notifications": True,
            "token": "gnagna",
            "marketingEmailSubscription": True,
        }

        response = client.post("/native/v1/account", json=data)
        assert response.status_code == 204, response.json

        user = User.query.first()
        assert Token.query.filter_by(user=user).first().value == f"performance-tests_email-validation_{user.id}"


class UserProfileUpdateTest:
    identifier = "email@example.com"

    def test_update_user_profile(self, app, client):
        password = "some_random_string"
        user = users_factories.UserFactory(email=self.identifier, password=password)

        client.with_token(user.email)
        response = client.post(
            "/native/v1/profile",
            json={
                "subscriptions": {"marketingPush": True, "marketingEmail": False},
            },
        )

        assert response.status_code == 200

        user = User.query.filter_by(email=self.identifier).first()

        assert user.get_notification_subscriptions().marketing_push
        assert not user.get_notification_subscriptions().marketing_email
        assert len(push_testing.requests) == 2

    def test_unsubscribe_push_notifications(self, client, app):
        user = users_factories.UserFactory(email=self.identifier)

        client.with_token(email=self.identifier)
        response = client.post(
            "/native/v1/profile", json={"subscriptions": {"marketingPush": False, "marketingEmail": False}}
        )

        assert response.status_code == 200

        user = User.query.filter_by(email=self.identifier).first()
        assert not user.get_notification_subscriptions().marketing_push
        assert not user.get_notification_subscriptions().marketing_email

        assert len(push_testing.requests) == 1

        push_request = push_testing.requests[0]
        assert push_request == {"user_id": user.id}

    @override_settings(BATCH_SECRET_API_KEY="coucou-la-cle")
    @override_settings(PUSH_NOTIFICATION_BACKEND="pcapi.notifications.push.backends.batch.BatchBackend")
    def test_unsubscribe_push_notifications_with_batch(self, client, app, cloud_task_client):
        users_factories.UserFactory(email=self.identifier)

        with patch("pcapi.notifications.push.backends.batch.requests.delete") as mock_delete:
            mock_delete.return_value.status_code = 200

            client.with_token(email=self.identifier)
            response = client.post(
                "/native/v1/profile", json={"subscriptions": {"marketingPush": False, "marketingEmail": False}}
            )

            assert response.status_code == 200
            assert mock_delete.call_count == 2  # Android + iOS

    def test_update_user_profile_reset_recredit_amount_to_show(self, client, app):
        user = users_factories.UnderageBeneficiaryFactory(email=self.identifier, recreditAmountToShow=30)

        client.with_token(email=self.identifier)
        response = client.post("/native/v1/reset_recredit_amount_to_show")

        assert response.status_code == 200
        assert user.recreditAmountToShow is None


class UpdateUserEmailTest:
    identifier = "email@example.com"

    def test_update_user_email(self, app, client):
        new_email = "updated_" + self.identifier
        password = "some_random_string"
        user = users_factories.UserFactory(email=self.identifier, password=password)

        client.with_token(user.email)
        response = client.post(
            "/native/v1/profile/update_email",
            json={
                "email": new_email,
                "password": password,
            },
        )

        assert response.status_code == 204

        user = User.query.filter_by(email=self.identifier).first()
        assert user.email == self.identifier  # email not updated until validation link is used
        assert len(mails_testing.outbox) == 2  # one email to the current address, another to the new

        # extract new email from activation link, which is a firebase
        # dynamic link meaning that the real url needs to be extracted
        # from it.
        activation_email = mails_testing.outbox[-1]
        confirmation_link = urlparse(activation_email.sent_data["params"]["CONFIRMATION_LINK"])
        base_url = parse_qs(confirmation_link.query)["link"][0]
        base_url_params = parse_qs(urlparse(base_url).query)

        assert {"new_email", "token", "expiration_timestamp"} <= base_url_params.keys()
        assert base_url_params["new_email"] == [new_email]

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
        "email,password",
        [
            ("new@example.com", "not_the_users_password"),
            ("invalid.password@format.com", "short"),
            ("not_an_email", "some_random_string"),
        ],
    )
    def test_update_email_errors(self, client, app, email, password):
        user = users_factories.UserFactory(email=self.identifier)

        client.with_token(user.email)
        response = client.post(
            "/native/v1/profile/update_email",
            json={
                "email": email,
                "password": password,
            },
        )

        assert response.status_code == 400

        user = User.query.filter_by(email=self.identifier).first()
        assert user.email == self.identifier
        assert not mails_testing.outbox

    def test_update_email_existing_email(self, app, client):
        """
        Test that if the email already exists, an OK response is sent
        but nothing is sent (avoid user enumeration).
        """
        user = users_factories.UserFactory(email=self.identifier)
        other_user = users_factories.UserFactory(email="other_" + self.identifier)

        client.with_token(user.email)
        response = client.post(
            "/native/v1/profile/update_email",
            json={
                "email": other_user.email,
                "password": "does_not_matter",
            },
        )

        assert response.status_code == 204

        user = User.query.filter_by(email=self.identifier).first()
        assert user.email == self.identifier
        assert not mails_testing.outbox

    @override_settings(MAX_EMAIL_UPDATE_ATTEMPTS=1)
    def test_update_email_too_many_attempts(self, app, client):
        """
        Test that a user cannot request more than
        MAX_EMAIL_UPDATE_ATTEMPTS email update change within the last
        N days.
        """
        self.send_two_requests(client, "EMAIL_UPDATE_ATTEMPTS_LIMIT")

    @override_settings(MAX_EMAIL_UPDATE_ATTEMPTS=2)
    def test_token_exists(self, app, client):
        """
        Test that the expected error code is sent back when a token
        already exists.

        Note: override MAX_EMAIL_UPDATE_ATTEMPTS to avoid any
        EMAIL_UPDATE_ATTEMPTS_LIMIT error.
        """
        self.send_two_requests(client, "TOKEN_EXISTS")

    def send_two_requests(self, client, error_code):
        password = "some_random_string"
        user = users_factories.UserFactory(email=self.identifier, password=password)

        client.with_token(user.email)
        response = client.post(
            "/native/v1/profile/update_email",
            json={
                "email": "updated_" + user.email,
                "password": password,
            },
        )

        assert response.status_code == 204

        client.with_token(user.email)
        response = client.post(
            "/native/v1/profile/update_email",
            json={
                "email": "updated_twice_" + user.email,
                "password": "does_not_matter",
            },
        )

        assert response.status_code == 400
        assert response.json["code"] == error_code


class ValidateEmailTest:
    old_email = "old@email.com"
    new_email = "new@email.com"

    def test_validate_email(self, app, client):
        user = users_factories.UserFactory(email=self.old_email)

        response = self.send_request_with_token(client, user.email)
        assert response.status_code == 204

        user = User.query.get(user.id)
        assert user.email == self.new_email

    def test_email_exists(self, app, client):
        """
        Test that if the email already exists, an OK response is sent
        but nothing is changed (avoid user enumeration).
        """
        user = users_factories.UserFactory(email=self.old_email)
        users_factories.UserFactory(email=self.new_email, isEmailValidated=True)

        response = self.send_request_with_token(client, user.email)

        assert response.status_code == 204

        user = User.query.get(user.id)
        assert user.email == self.old_email

    def test_email_invalid(self, app, client):
        response = self.send_request_with_token(client, "not_an_email")

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_EMAIL"

    def test_expired_token(self, app, client):
        user = users_factories.UserFactory(email=self.old_email)
        users_factories.UserFactory(email=self.new_email, isEmailValidated=True)

        response = self.send_request_with_token(client, user.email, expiration_delta=-timedelta(hours=1))

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_TOKEN"

        user = User.query.get(user.id)
        assert user.email == self.old_email

    def send_request_with_token(self, client, email, expiration_delta=None):
        if not expiration_delta:
            expiration_delta = timedelta(hours=1)

        expiration = int((datetime.utcnow() + expiration_delta).timestamp())
        token_payload = {"exp": expiration, "current_email": email, "new_email": self.new_email}

        token = jwt.encode(
            token_payload,
            settings.JWT_SECRET_KEY,  # type: ignore # known as str in build assertion
            algorithm=ALGORITHM_HS_256,
        )

        return client.with_token(email).put("/native/v1/profile/validate_email", json={"token": token})


class GetTokenExpirationTest:
    email = "some@email.com"

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

        expiration_date = datetime.utcnow() + timedelta(hours=15)
        key = email_update.get_no_active_token_key(user)

        app.redis_client.incr(key)
        app.redis_client.expireat(key, expiration_date)

        response = client.with_token(user.email).get("/native/v1/profile/token_expiration")
        assert response.status_code == 200

        expiration = datetime.fromisoformat(response.json["expiration"])
        delta = abs(expiration - expiration_date)
        assert delta < timedelta(seconds=2)

    def test_no_token(self, app, client):
        user = users_factories.UserFactory(email=self.email)

        response = client.with_token(user.email).get("/native/v1/profile/token_expiration")

        assert response.status_code == 200
        assert response.json["expiration"] is None


class CulturalSurveyTest:
    identifier = "email@example.com"
    FROZEN_TIME = ""
    UUID = uuid.uuid4()

    @freeze_time("2018-06-01 14:44")
    def test_user_finished_the_cultural_survey(self, app):
        user, test_client = create_user_and_test_client(
            app,
            email=self.identifier,
            needsToFillCulturalSurvey=True,
            culturalSurveyId=None,
            culturalSurveyFilledDate=None,
        )

        response = test_client.post(
            "/native/v1/me/cultural_survey",
            json={
                "needsToFillCulturalSurvey": False,
                "culturalSurveyId": self.UUID,
            },
        )

        assert response.status_code == 204

        user = User.query.one()
        assert user.needsToFillCulturalSurvey == False
        assert user.culturalSurveyId == self.UUID
        assert user.culturalSurveyFilledDate == datetime(2018, 6, 1, 14, 44)

    @freeze_time("2018-06-01 14:44")
    def test_user_gave_up_the_cultural_survey(self, app):
        user, test_client = create_user_and_test_client(
            app,
            email=self.identifier,
            needsToFillCulturalSurvey=False,
            culturalSurveyId=None,
            culturalSurveyFilledDate=None,
        )

        response = test_client.post(
            "/native/v1/me/cultural_survey",
            json={
                "needsToFillCulturalSurvey": False,
                "culturalSurveyId": None,
            },
        )

        assert response.status_code == 204

        user = User.query.one()
        assert user.needsToFillCulturalSurvey == False
        assert user.culturalSurveyId == None
        assert user.culturalSurveyFilledDate == None

    def test_user_fills_again_the_cultural_survey(self, app):
        user, test_client = create_user_and_test_client(
            app,
            email=self.identifier,
            needsToFillCulturalSurvey=False,
            culturalSurveyId=self.UUID,
            culturalSurveyFilledDate=datetime(2016, 5, 1, 14, 44),
        )
        new_uuid = uuid.uuid4()

        response = test_client.post(
            "/native/v1/me/cultural_survey",
            json={
                "needsToFillCulturalSurvey": False,
                "culturalSurveyId": new_uuid,
            },
        )

        assert response.status_code == 204

        user = User.query.one()
        assert user.needsToFillCulturalSurvey == False
        assert user.culturalSurveyId == new_uuid
        assert user.culturalSurveyFilledDate > datetime(2016, 5, 1, 14, 44)


class ResendEmailValidationTest:
    def test_resend_email_validation(self, client, app):
        user = users_factories.UserFactory(isEmailValidated=False)

        response = client.post("/native/v1/resend_email_validation", json={"email": user.email})

        assert response.status_code == 204
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.EMAIL_CONFIRMATION.value
        )

    def test_for_already_validated_email_does_sent_passsword_reset(self, client, app):
        user = users_factories.UserFactory(isEmailValidated=True)

        response = client.post("/native/v1/resend_email_validation", json={"email": user.email})

        assert response.status_code == 204
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.NEW_PASSWORD_REQUEST.value
        )

    def test_for_unknown_mail_does_nothing(self, client, app):
        response = client.post("/native/v1/resend_email_validation", json={"email": "aijfioern@mlks.com"})

        assert response.status_code == 204
        assert not mails_testing.outbox

    def test_for_deactivated_account_does_nothhing(self, client, app):
        user = users_factories.UserFactory(isEmailValidated=True, isActive=False)

        response = client.post("/native/v1/resend_email_validation", json={"email": user.email})

        assert response.status_code == 204
        assert not mails_testing.outbox


class ShowEligibleCardTest:
    @pytest.mark.parametrize("age,expected", [(17, False), (18, True), (19, False)])
    def test_against_different_age(self, age, expected):
        date_of_birth = datetime.utcnow() - relativedelta(years=age, days=5)
        date_of_creation = datetime.utcnow() - relativedelta(years=4)
        user = users_factories.UserFactory.build(dateOfBirth=date_of_birth, dateCreated=date_of_creation)
        assert account_serializers.UserProfileResponse._show_eligible_card(user) == expected

    @pytest.mark.parametrize("beneficiary,expected", [(False, True), (True, False)])
    def test_against_beneficiary(self, beneficiary, expected):
        date_of_birth = datetime.utcnow() - relativedelta(years=18, days=5)
        date_of_creation = datetime.utcnow() - relativedelta(years=4)
        roles = [UserRole.BENEFICIARY] if beneficiary else []
        user = users_factories.UserFactory.build(
            dateOfBirth=date_of_birth,
            dateCreated=date_of_creation,
            roles=roles,
        )
        assert account_serializers.UserProfileResponse._show_eligible_card(user) == expected

    def test_user_eligible_but_created_after_18(self):
        date_of_birth = datetime.utcnow() - relativedelta(years=18, days=5)
        date_of_creation = datetime.utcnow()
        user = users_factories.UserFactory.build(dateOfBirth=date_of_birth, dateCreated=date_of_creation)
        assert account_serializers.UserProfileResponse._show_eligible_card(user) == False


class SendPhoneValidationCodeTest:
    def test_send_phone_validation_code(self, client, app):
        user = users_factories.UserFactory(phoneNumber="+33601020304")
        client.with_token(email=user.email)

        response = client.post("/native/v1/send_phone_validation_code")

        assert response.status_code == 204

        assert int(app.redis_client.get(f"sent_SMS_counter_user_{user.id}")) == 1

        token = Token.query.filter_by(userId=user.id, type=TokenType.PHONE_VALIDATION).first()

        assert token.expirationDate >= datetime.utcnow() + timedelta(minutes=2)
        assert token.expirationDate < datetime.utcnow() + timedelta(minutes=30)

        assert sms_testing.requests == [
            {"recipient": "+33601020304", "content": f"{token.value} est ton code de confirmation pass Culture"}
        ]
        assert len(token.value) == 6
        assert 0 <= int(token.value) < 1000000

        # validate phone number with generated code
        response = client.post("/native/v1/validate_phone_number", json={"code": token.value})

        assert response.status_code == 204
        user = User.query.get(user.id)
        assert user.is_phone_validated

    @pytest.mark.parametrize(
        "age,eligibility_type",
        [
            (15, EligibilityType.UNDERAGE),
            (16, EligibilityType.UNDERAGE),
            (17, EligibilityType.UNDERAGE),
            (18, EligibilityType.AGE18),
            (19, None),
        ],
    )
    @override_settings(MAX_SMS_SENT_FOR_PHONE_VALIDATION=1)
    def test_send_phone_validation_code_too_many_attempts(self, client, app, age, eligibility_type):
        user = users_factories.UserFactory(
            phoneNumber="+33601020304",
            dateOfBirth=datetime.utcnow() - relativedelta(years=age, days=5),
        )
        client.with_token(email=user.email)

        response = client.post("/native/v1/send_phone_validation_code")
        assert response.status_code == 204

        response = client.post("/native/v1/send_phone_validation_code")
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
        assert fraud_check.eligibilityType == eligibility_type

        content = fraud_check.resultContent
        expected_reason = "Le nombre maximum de sms envoyés est atteint"
        assert content["source"] == fraud_models.InternalReviewSource.SMS_SENDING_LIMIT_REACHED.value
        assert content["message"] == expected_reason
        assert content["phone_number"] == "+33601020304"

    def test_send_phone_validation_code_already_beneficiary(self, client, app):
        user = users_factories.BeneficiaryGrant18Factory(
            isEmailValidated=True, phoneNumber="+33601020304", roles=[UserRole.BENEFICIARY]
        )
        client.with_token(email=user.email)

        response = client.post("/native/v1/send_phone_validation_code")

        assert response.status_code == 400

        assert not Token.query.filter_by(userId=user.id).first()

    def test_send_phone_validation_code_for_new_phone_with_already_beneficiary(self, client, app):
        user = users_factories.BeneficiaryGrant18Factory(
            isEmailValidated=True, phoneNumber="+33601020304", roles=[UserRole.BENEFICIARY]
        )
        client.with_token(email=user.email)

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33102030405"})

        assert response.status_code == 400

        assert not Token.query.filter_by(userId=user.id).first()
        db.session.refresh(user)
        assert user.phoneNumber == "+33601020304"

    def test_send_phone_validation_code_for_new_phone_updates_phone(self, client, app):
        user = users_factories.UserFactory(isEmailValidated=True, phoneNumber="+33601020304")
        client.with_token(email=user.email)

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33102030405"})

        assert response.status_code == 204

        assert Token.query.filter_by(userId=user.id).first()
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

    @pytest.mark.parametrize(
        "age,eligibility_type",
        [
            (15, EligibilityType.UNDERAGE),
            (16, EligibilityType.UNDERAGE),
            (17, EligibilityType.UNDERAGE),
            (18, EligibilityType.AGE18),
            (19, None),
        ],
    )
    def test_send_phone_validation_code_for_new_validated_duplicated_phone_number(
        self, client, app, age, eligibility_type
    ):
        orig_user = users_factories.UserFactory(
            isEmailValidated=True,
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
            phoneNumber="+33102030405",
        )
        user = users_factories.UserFactory(
            isEmailValidated=True,
            phoneNumber="+33601020304",
            dateOfBirth=datetime.utcnow() - relativedelta(years=age, days=5),
        )
        client.with_token(email=user.email)

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33102030405"})

        assert response.status_code == 400

        assert not Token.query.filter_by(userId=user.id).first()
        db.session.refresh(user)
        assert user.phoneNumber == "+33601020304"
        assert response.json == {"message": "Le numéro de téléphone est invalide", "code": "INVALID_PHONE_NUMBER"}

        # check that a fraud check has been created
        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            userId=user.id,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            thirdPartyId=f"PC-{user.id}",
            status=fraud_models.FraudCheckStatus.KO,
        ).one_or_none()

        assert fraud_check is not None
        assert fraud_check.eligibilityType == eligibility_type

        content = fraud_check.resultContent
        assert content["source"] == fraud_models.InternalReviewSource.PHONE_ALREADY_EXISTS.value
        assert content["message"] == f"Le numéro est déjà utilisé par l'utilisateur {orig_user.id}"
        assert content["phone_number"] == "+33102030405"

        assert (
            subscription_api.get_phone_validation_subscription_item(user, EligibilityType.AGE18).status
            == subscription_models.SubscriptionItemStatus.KO
        )

    @override_settings(BLACKLISTED_SMS_RECIPIENTS={"+33607080900"})
    def test_update_phone_number_with_blocked_phone_number(self, client, app):
        user = users_factories.UserFactory(isEmailValidated=True, phoneNumber="+33601020304")
        client.with_token(email=user.email)

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33607080900"})

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_PHONE_NUMBER"

        assert not Token.query.filter_by(userId=user.id).first()
        db.session.refresh(user)
        assert user.phoneNumber == "+33601020304"

    def test_send_phone_validation_code_with_malformed_number(self, client, app):
        # user's phone number should be in international format (E.164): +33601020304
        user = users_factories.UserFactory(isEmailValidated=True, phoneNumber="0601020304")
        client.with_token(email=user.email)

        response = client.post("/native/v1/send_phone_validation_code")

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_PHONE_NUMBER"
        assert not Token.query.filter_by(userId=user.id).first()

    def test_send_phone_validation_code_with_non_french_number(self, client, app):
        user = users_factories.UserFactory(isEmailValidated=True, phoneNumber="+46766123456")
        client.with_token(email=user.email)

        response = client.post("/native/v1/send_phone_validation_code")

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_PHONE_NUMBER"
        assert not Token.query.filter_by(userId=user.id).first()

    def test_update_phone_number_with_non_french_number(self, client, app):
        user = users_factories.UserFactory(isEmailValidated=True, phoneNumber="+46766123456")
        client.with_token(email=user.email)

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+46766987654"})

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_PHONE_NUMBER"
        assert not Token.query.filter_by(userId=user.id).first()

        db.session.refresh(user)
        assert user.phoneNumber == "+46766123456"

    @pytest.mark.parametrize(
        "age,eligibility_type",
        [
            (15, EligibilityType.UNDERAGE),
            (16, EligibilityType.UNDERAGE),
            (17, EligibilityType.UNDERAGE),
            (18, EligibilityType.AGE18),
            (19, None),
        ],
    )
    @override_settings(BLACKLISTED_SMS_RECIPIENTS={"+33601020304"})
    def test_blocked_phone_number(self, client, app, age, eligibility_type):
        user = users_factories.UserFactory(
            phoneNumber="+33601020304",
            dateOfBirth=datetime.utcnow() - relativedelta(years=age, days=5),
        )
        client.with_token(email=user.email)

        response = client.post("/native/v1/send_phone_validation_code")

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_PHONE_NUMBER"

        assert not Token.query.filter_by(userId=user.id).first()
        db.session.refresh(user)
        assert user.phoneNumber == "+33601020304"

        # check that a fraud check has been created
        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            userId=user.id,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            thirdPartyId=f"PC-{user.id}",
            status=fraud_models.FraudCheckStatus.KO,
        ).one_or_none()

        assert fraud_check is not None
        assert fraud_check.eligibilityType == eligibility_type

        content = fraud_check.resultContent
        assert content["source"] == fraud_models.InternalReviewSource.BLACKLISTED_PHONE_NUMBER.value
        assert content["message"] == "Le numéro saisi est interdit"
        assert content["phone_number"] == "+33601020304"


class ValidatePhoneNumberTest:
    def test_validate_phone_number(self, client, app):
        user = users_factories.UserFactory(
            phoneNumber="+33607080900",
            subscriptionState=users_models.SubscriptionState.email_validated,
        )
        client.with_token(email=user.email)
        token = create_phone_validation_token(user)

        # try one attempt with wrong code
        client.post("/native/v1/validate_phone_number", {"code": "wrong code"})
        response = client.post("/native/v1/validate_phone_number", {"code": token.value})

        assert response.status_code == 204
        user = User.query.get(user.id)
        assert user.is_phone_validated
        assert user.is_subscriptionState_phone_validated()
        assert not user.has_beneficiary_role

        token = Token.query.filter_by(userId=user.id, type=TokenType.PHONE_VALIDATION).first()

        assert not token

        assert int(app.redis_client.get(f"phone_validation_attempts_user_{user.id}")) == 2

    def test_validate_phone_number_and_become_beneficiary(self, client, app):
        user = users_factories.UserFactory(
            phoneNumber="+33607080900",
            subscriptionState=users_models.SubscriptionState.email_validated,
            activity="Lycéen",
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.OK
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.HONOR_STATEMENT, status=fraud_models.FraudCheckStatus.OK
        )

        client.with_token(email=user.email)
        token = create_phone_validation_token(user)

        response = client.post("/native/v1/validate_phone_number", {"code": token.value})

        assert response.status_code == 204
        user = User.query.get(user.id)
        assert user.is_phone_validated
        assert user.is_subscriptionState_phone_validated()
        assert user.has_beneficiary_role

    @override_settings(MAX_PHONE_VALIDATION_ATTEMPTS=1)
    def test_validate_phone_number_too_many_attempts(self, client, app):
        user = users_factories.UserFactory(
            phoneNumber="+33607080900",
            dateOfBirth=datetime.utcnow() - relativedelta(years=18, days=5),
            subscriptionState=users_models.SubscriptionState.email_validated,
        )
        client.with_token(email=user.email)
        token = create_phone_validation_token(user)

        response = client.post("/native/v1/validate_phone_number", {"code": "wrong code"})
        response = client.post("/native/v1/validate_phone_number", {"code": token.value})

        assert response.status_code == 400
        assert response.json["message"] == "Le nombre de tentatives maximal est dépassé"
        assert response.json["code"] == "TOO_MANY_VALIDATION_ATTEMPTS"

        db.session.refresh(user)
        assert not user.is_phone_validated
        assert user.is_subscriptionState_phone_validation_ko

        attempts_count = int(app.redis_client.get(f"phone_validation_attempts_user_{user.id}"))
        assert attempts_count == 1

        # check that a fraud check has been created
        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            userId=user.id,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            thirdPartyId=f"PC-{user.id}",
        ).one_or_none()

        assert fraud_check is not None
        assert fraud_check.eligibilityType == EligibilityType.AGE18

        expected_reason = f"Le nombre maximum de tentatives de validation est atteint: {attempts_count}"
        content = fraud_check.resultContent
        assert content["source"] == fraud_models.InternalReviewSource.PHONE_VALIDATION_ATTEMPTS_LIMIT_REACHED.value
        assert content["message"] == expected_reason
        assert content["phone_number"] == "+33607080900"

    def test_wrong_code(self, client, app):
        user = users_factories.UserFactory(
            phoneNumber="+33607080900",
            subscriptionState=users_models.SubscriptionState.email_validated,
        )
        client.with_token(email=user.email)
        create_phone_validation_token(user)

        response = client.post("/native/v1/validate_phone_number", {"code": "mauvais-code"})

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_VALIDATION_CODE"

        assert not User.query.get(user.id).is_phone_validated
        assert user.is_subscriptionState_phone_validation_ko
        assert Token.query.filter_by(userId=user.id, type=TokenType.PHONE_VALIDATION).first()

    def test_expired_code(self, client, app):
        user = users_factories.UserFactory(
            phoneNumber="+33607080900",
            subscriptionState=users_models.SubscriptionState.email_validated,
        )
        token = create_phone_validation_token(user)

        with freeze_time(datetime.utcnow() + timedelta(minutes=20)):
            client.with_token(email=user.email)
            response = client.post("/native/v1/validate_phone_number", {"code": token.value})

        assert response.status_code == 400
        assert response.json["code"] == "EXPIRED_VALIDATION_CODE"

        assert not User.query.get(user.id).is_phone_validated
        assert user.is_subscriptionState_phone_validation_ko
        assert Token.query.filter_by(userId=user.id, type=TokenType.PHONE_VALIDATION).first()

    @override_settings(BLACKLISTED_SMS_RECIPIENTS={"+33607080900"})
    def test_blocked_phone_number(self, client, app):
        user = users_factories.UserFactory(
            phoneNumber="+33607080900",
            subscriptionState=users_models.SubscriptionState.email_validated,
        )
        token = create_phone_validation_token(user)

        client.with_token(email=user.email)
        response = client.post("/native/v1/validate_phone_number", {"code": token.value})

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_PHONE_NUMBER"

        assert not User.query.get(user.id).is_phone_validated
        assert user.is_subscriptionState_phone_validation_ko
        assert Token.query.filter_by(userId=user.id, type=TokenType.PHONE_VALIDATION).first()

    def test_validate_phone_number_with_non_french_number(self, client, app):
        user = users_factories.UserFactory(
            phoneNumber="+46766123456",
            subscriptionState=users_models.SubscriptionState.email_validated,
        )
        token = create_phone_validation_token(user)

        client.with_token(email=user.email)
        response = client.post("/native/v1/validate_phone_number", {"code": token.value})

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_PHONE_NUMBER"

        assert not User.query.get(user.id).is_phone_validated
        assert user.is_subscriptionState_phone_validation_ko
        assert Token.query.filter_by(userId=user.id, type=TokenType.PHONE_VALIDATION).first()

    def test_validate_phone_number_with_already_validated_phone(self, client, app):
        users_factories.UserFactory(
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
            phoneNumber="+33607080900",
            subscriptionState=users_models.SubscriptionState.email_validated,
        )
        user = users_factories.UserFactory(phoneNumber="+33607080900")
        client.with_token(email=user.email)
        token = create_phone_validation_token(user)

        # try one attempt with wrong code
        response = client.post("/native/v1/validate_phone_number", {"code": token.value})

        assert response.status_code == 400
        user = User.query.get(user.id)
        assert not user.is_phone_validated
        assert user.is_subscriptionState_phone_validation_ko

        token = Token.query.filter_by(userId=user.id, type=TokenType.PHONE_VALIDATION).first()
        assert not token

        assert int(app.redis_client.get(f"phone_validation_attempts_user_{user.id}")) == 1


class SuspendAccountTest:
    def test_suspend_account(self, client, app):
        booking = booking_factories.IndividualBookingFactory()
        user = booking.individualBooking.user

        client.with_token(email=user.email)
        response = client.post("/native/v1/account/suspend")

        assert response.status_code == 204
        assert booking.status == BookingStatus.CANCELLED
        db.session.refresh(user)
        assert not user.isActive
        assert user.suspension_reason == SuspensionReason.UPON_USER_REQUEST
        assert user.suspension_date
        assert len(user.suspension_history) == 1
        assert user.suspension_history[0].userId == user.id
        assert user.suspension_history[0].actorUserId == user.id

    def test_suspend_suspended_account(self, client, app):
        # Ensure that a beneficiary user can't change the reason for being suspended
        user = users_factories.BeneficiaryGrant18Factory(isActive=False)
        user_suspension = users_factories.UserSuspensionFactory(user=user)

        client.with_token(email=user.email)
        response = client.post("/native/v1/account/suspend")

        # Any API call is forbidden for suspended user
        assert response.status_code == 403
        db.session.refresh(user)
        assert not user.isActive
        assert user.suspension_reason == user_suspension.reasonCode
        assert len(user.suspension_history) == 1


class ProfilingFraudScoreTest:

    USER_PROFILING_URL = "https://example.com/path"

    # Remove parametrize() on session_id_key after session_id is removed and only sessionId kept
    @pytest.mark.parametrize("session_id_key", ["sessionId", "session_id"])
    @pytest.mark.parametrize(
        "session_id_value", ["b0c9ab58-cdfb-4461-a771-a00683b85bd2", "09cb5fa1c9894252b147de4a37d01f30"]
    )
    @override_settings(USER_PROFILING_URL=USER_PROFILING_URL)
    def test_profiling_fraud_score_call(self, client, requests_mock, session_id_key, session_id_value):
        user = users_factories.UserFactory(
            subscriptionState=users_models.SubscriptionState.phone_validated,
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
        )
        matcher = requests_mock.register_uri(
            "POST",
            settings.USER_PROFILING_URL,
            json=user_profiling_fixtures.CORRECT_RESPONSE,
            status_code=200,
        )
        client.with_token(user.email)

        response = client.post(
            "/native/v1/user_profiling", json={session_id_key: session_id_value, "agentType": "browser_mobile"}
        )
        assert response.status_code == 204
        assert matcher.call_count == 1
        assert user.is_subscriptionState_user_profiling_validated()

        assert fraud_models.BeneficiaryFraudCheck.query.count() == 1
        fraud_check = fraud_models.BeneficiaryFraudCheck.query.first()
        assert fraud_check.userId == user.id
        assert fraud_check.type == fraud_models.FraudCheckType.USER_PROFILING
        assert fraud_check.eligibilityType == None
        assert fraud_check.status == fraud_models.FraudCheckStatus.OK

    @override_settings(USER_PROFILING_URL=USER_PROFILING_URL)
    def test_profiling_fraud_score_call_error(self, client, requests_mock, caplog):
        user = users_factories.UserFactory(
            subscriptionState=users_models.SubscriptionState.phone_validated,
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
        )
        matcher = requests_mock.register_uri(
            "POST",
            settings.USER_PROFILING_URL,
            json=user_profiling_fixtures.PARAMETER_ERROR_RESPONSE,
            status_code=500,
        )
        client.with_token(user.email)
        response = client.post(
            "/native/v1/user_profiling", json={"sessionId": "randomsessionid", "agentType": "agent_mobile"}
        )
        assert response.status_code == 204
        assert matcher.call_count == 1
        assert caplog.record_tuples == [
            ("pcapi.routes.native.v1.account", 40, "Error while retrieving user profiling infos")
        ]

    @override_settings(USER_PROFILING_URL=USER_PROFILING_URL)
    def test_profiling_fraud_score_user_without_birth_date(self, client, requests_mock, caplog):
        user = users_factories.UserFactory(
            dateOfBirth=None,
            subscriptionState=users_models.SubscriptionState.phone_validated,
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
        )
        matcher = requests_mock.register_uri(
            "POST",
            settings.USER_PROFILING_URL,
            json=user_profiling_fixtures.CORRECT_RESPONSE,
            status_code=200,
        )
        client.with_token(user.email)

        with caplog.at_level(logging.INFO):
            response = client.post(
                "/native/v1/user_profiling", json={"sessionId": "randomsessionid", "agentType": "agent_mobile"}
            )
        assert response.status_code == 204
        assert matcher.call_count == 1
        assert len(caplog.records) >= 2
        assert caplog.record_tuples[0][-1] == "External service called"
        assert caplog.record_tuples[1][-1].startswith("Success when profiling user:")
        assert fraud_models.BeneficiaryFraudCheck.query.count() == 1
        fraud_check = fraud_models.BeneficiaryFraudCheck.query.first()
        assert fraud_check.userId == user.id
        assert fraud_check.type == fraud_models.FraudCheckType.USER_PROFILING
        assert fraud_check.eligibilityType == None
        assert fraud_check.status == fraud_models.FraudCheckStatus.OK

    @pytest.mark.parametrize("session_id_value", ["gdavmoioeuboaobç!p'è", "", "a" * 150])
    @override_settings(USER_PROFILING_URL=USER_PROFILING_URL)
    def test_profiling_session_id_invalid(self, client, requests_mock, session_id_value):
        user = users_factories.UserFactory(subscriptionState=users_models.SubscriptionState.phone_validated)
        matcher = requests_mock.register_uri(
            "POST",
            settings.USER_PROFILING_URL,
            json=user_profiling_fixtures.CORRECT_RESPONSE,
            status_code=200,
        )
        client.with_token(user.email)
        response = client.post(
            "/native/v1/user_profiling", json={"sessionId": session_id_value, "agentType": "agent_mobile"}
        )
        assert response.status_code == 400
        assert matcher.call_count == 0

    @override_settings(USER_PROFILING_URL=USER_PROFILING_URL)
    @pytest.mark.parametrize(
        "risk_rating,expected_check_status",
        (
            (fraud_models.UserProfilingRiskRating.HIGH, fraud_models.FraudCheckStatus.KO),
            (fraud_models.UserProfilingRiskRating.MEDIUM, fraud_models.FraudCheckStatus.SUSPICIOUS),
        ),
    )
    def test_fraud_result_on_risky_user_profiling(self, client, requests_mock, risk_rating, expected_check_status):
        user = users_factories.UserFactory(
            subscriptionState=users_models.SubscriptionState.phone_validated,
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
        )
        session_id = "8663ac09-db2a-46a1-9ccd-49a07d5cd7ae"
        payload = fraud_factories.UserProfilingFraudDataFactory(risk_rating=risk_rating).dict()
        payload["event_datetime"] = payload["event_datetime"].isoformat()  # because datetime is not json serializable
        payload["risk_rating"] = payload["risk_rating"].value  # because Enum is not json serializable
        requests_mock.register_uri(
            "POST",
            settings.USER_PROFILING_URL,
            json=payload,
            status_code=200,
        )
        client.with_token(user.email)

        response = client.post("/native/v1/user_profiling", json={"sessionId": session_id, "agentType": "agent_mobile"})

        assert response.status_code == 204

        assert len(user.subscriptionMessages) == 1
        sub_message = user.subscriptionMessages[0]
        assert sub_message.userMessage == "Ton inscription n'a pas pu aboutir."
        assert user.is_subscriptionState_user_profiling_ko()

        assert fraud_models.BeneficiaryFraudCheck.query.count() == 1
        fraud_check = fraud_models.BeneficiaryFraudCheck.query.first()
        assert fraud_check.userId == user.id
        assert fraud_check.type == fraud_models.FraudCheckType.USER_PROFILING
        assert fraud_check.eligibilityType == None
        assert fraud_check.status == expected_check_status

    @override_settings(USER_PROFILING_URL=USER_PROFILING_URL)
    @pytest.mark.parametrize(
        "risk_rating",
        (
            fraud_models.UserProfilingRiskRating.TRUSTED,
            fraud_models.UserProfilingRiskRating.NEUTRAL,
            fraud_models.UserProfilingRiskRating.LOW,
        ),
    )
    def test_no_fraud_result_on_safe_user_profiling(self, client, requests_mock, risk_rating):
        user = users_factories.UserFactory(
            subscriptionState=users_models.SubscriptionState.phone_validated,
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
        )
        payload = fraud_factories.UserProfilingFraudDataFactory(risk_rating=risk_rating).dict()
        payload["event_datetime"] = payload["event_datetime"].isoformat()  # because datetime is not json serializable
        payload["risk_rating"] = payload["risk_rating"].value  # because Enum is not json serializable
        requests_mock.register_uri(
            "POST",
            settings.USER_PROFILING_URL,
            json=payload,
            status_code=200,
        )
        client.with_token(user.email)
        session_id = "ffd4ad0f-be8c-4b1e-97ec-0fdd5e4edae0"

        response = client.post("/native/v1/user_profiling", json={"sessionId": session_id, "agentType": "agent_mobile"})

        assert response.status_code == 204
        assert (
            fraud_models.BeneficiaryFraudResult.query.filter(fraud_models.BeneficiaryFraudResult.user == user).count()
            == 0
        )
        assert user.is_subscriptionState_user_profiling_validated()

    @override_features(ENABLE_USER_PROFILING=False)
    def test_no_profiling_performed_when_disabled(self, client, requests_mock):
        user = users_factories.UserFactory(
            subscriptionState=users_models.SubscriptionState.phone_validated,
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
        )
        matcher = requests_mock.register_uri("POST", settings.USER_PROFILING_URL)
        client.with_token(user.email)

        response = client.post(
            "/native/v1/user_profiling", json={"sessionId": "session_id_value", "agentType": "browser_mobile"}
        )
        assert response.status_code == 204
        assert matcher.call_count == 0

        assert fraud_models.BeneficiaryFraudCheck.query.count() == 0


class ProfilingSessionIdTest:
    def test_profiling_session_id(self, client):
        user = users_factories.UserFactory()

        client.with_token(user.email)

        session_ids = set()

        for _ in range(5):
            response = client.get("/native/v1/user_profiling/session_id")

            assert response.status_code == 200
            assert re.match("^[A-Za-z0-9_-]{10,128}$", response.json["sessionId"])

            session_ids.add(response.json["sessionId"])

        # Check that all session ids are different
        assert len(session_ids) == 5


class IdentificationSessionTest:
    @pytest.mark.parametrize("age", [15, 16, 17, 18])
    def test_request(self, client, ubble_mock, age):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=age, days=5))

        client.with_token(user.email)

        response = client.post("/native/v1/ubble_identification", json={"redirectUrl": "http://example.com/deeplink"})

        assert response.status_code == 200
        assert len(user.beneficiaryFraudChecks) == 1
        assert ubble_mock.call_count == 1

        check = user.beneficiaryFraudChecks[0]
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
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18, days=5))

        client.with_token(user.email)

        response = client.post("/native/v1/ubble_identification", json={"redirectUrl": "http://example.com/deeplink"})

        assert response.status_code == 503
        assert response.json["code"] == "IDCHECK_SERVICE_UNAVAILABLE"
        assert len(user.beneficiaryFraudChecks) == 0
        assert ubble_mock_connection_error.call_count == 1

    def test_request_ubble_http_error_status(self, client, ubble_mock_http_error_status):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18, days=5))

        client.with_token(user.email)

        response = client.post("/native/v1/ubble_identification", json={"redirectUrl": "http://example.com/deeplink"})

        assert response.status_code == 500
        assert response.json["code"] == "IDCHECK_SERVICE_ERROR"
        assert len(user.beneficiaryFraudChecks) == 0
        assert ubble_mock_http_error_status.call_count == 1

    @pytest.mark.parametrize(
        "fraud_check_status,ubble_status",
        [
            (fraud_models.FraudCheckStatus.PENDING, ubble_fraud_models.UbbleIdentificationStatus.PROCESSING),
            (fraud_models.FraudCheckStatus.OK, ubble_fraud_models.UbbleIdentificationStatus.PROCESSED),
            (fraud_models.FraudCheckStatus.KO, ubble_fraud_models.UbbleIdentificationStatus.PROCESSED),
        ],
    )
    def test_request_ubble_second_check_blocked(self, client, ubble_mock, fraud_check_status, ubble_status):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18, days=5))
        client.with_token(user.email)

        # Perform phone validation and user profiling
        user.phoneValidationStatus = PhoneValidationStatusType.VALIDATED
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent=fraud_factories.UserProfilingFraudDataFactory(
                risk_rating=fraud_models.UserProfilingRiskRating.TRUSTED
            ),
        )

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
        assert len(user.beneficiaryFraudChecks) == 2

    def test_request_ubble_second_check_after_first_aborted(self, client, ubble_mock):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18, days=5))
        client.with_token(user.email)

        # Perform phone validation and user profiling
        user.phoneValidationStatus = PhoneValidationStatusType.VALIDATED
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent=fraud_factories.UserProfilingFraudDataFactory(
                risk_rating=fraud_models.UserProfilingRiskRating.TRUSTED
            ),
        )

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
        check = sorted_fraud_checks[2]
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
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18, days=5))
        client.with_token(user.email)

        # Perform phone validation and user profiling
        user.phoneValidationStatus = PhoneValidationStatusType.VALIDATED
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent=fraud_factories.UserProfilingFraudDataFactory(
                risk_rating=fraud_models.UserProfilingRiskRating.TRUSTED
            ),
        )

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
            fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER,
        ],
    )
    def test_request_ubble_retry_not_allowed(self, client, ubble_mock, reason):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18, days=5))
        client.with_token(user.email)

        # Perform phone validation and user profiling
        user.phoneValidationStatus = PhoneValidationStatusType.VALIDATED
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent=fraud_factories.UserProfilingFraudDataFactory(
                risk_rating=fraud_models.UserProfilingRiskRating.TRUSTED
            ),
        )

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
        assert len(user.beneficiaryFraudChecks) == 2

    def test_allow_rerun_identification_from_started(self, client, ubble_mock):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18, days=5))
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
        assert len(user.beneficiaryFraudChecks) == 1
        assert ubble_mock.call_count == 0

        check = user.beneficiaryFraudChecks[0]
        assert check.type == fraud_models.FraudCheckType.UBBLE
        assert response.json["identificationUrl"] == expected_url


class AccountSecurityTest:
    def test_account_hacker_changes_password(self, client, app):
        """
        This scenario has been suggested by a security bug hunter: it is possible for a hacker to register with the
        email someone else registered earlier, before the hacked user clicks on email confirmation link. The hacker can
        change user's password this way.
        """
        assert User.query.first() is None
        data = {
            "appsFlyerPlatform": "web",
            "birthdate": "2004-01-01",
            "email": "patrick@example.com",
            "marketingEmailSubscription": True,
            "password": "User@1234",
            "postalCode": "",
            "token": "usertoken",
        }

        response = client.post("/native/v1/account", json=data)
        assert response.status_code == 204, response.json

        user = User.query.first()
        assert user is not None
        assert user.email == data["email"]
        assert user.isEmailValidated is False

        user_password = user.password

        hacker_data = data.copy()
        hacker_data.update(
            {
                "password": "Hacker@5678",
                "token": "hackertoken",
            }
        )

        hacker_response = client.post("/native/v1/account", json=hacker_data)
        assert hacker_response.status_code == 204, hacker_response.json

        assert User.query.count() == 1
        user = User.query.first()
        assert user.password == user_password
