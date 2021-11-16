from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from io import BytesIO
import logging
from pathlib import Path
from unittest.mock import patch
import uuid

from dateutil.relativedelta import relativedelta
from flask_jwt_extended.utils import create_access_token
from freezegun.api import freeze_time
from google.cloud import tasks_v2
import pytest

from pcapi import settings
from pcapi.core.bookings import factories as booking_factories
from pcapi.core.bookings.factories import CancelledIndividualBookingFactory
from pcapi.core.bookings.factories import IndividualBookingFactory
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
import pcapi.core.mails.testing as mails_testing
import pcapi.core.subscription.factories as subscription_factories
import pcapi.core.subscription.messages as subscription_messages
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import testing as users_testing
from pcapi.core.users.api import create_phone_validation_token
from pcapi.core.users.constants import SuspensionReason
from pcapi.core.users.factories import BeneficiaryImportFactory
from pcapi.core.users.factories import TokenFactory
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import PhoneValidationStatusType
from pcapi.core.users.models import Token
from pcapi.core.users.models import TokenType
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole
from pcapi.core.users.models import VOID_PUBLIC_NAME
from pcapi.core.users.repository import get_id_check_token
from pcapi.models import db
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.notifications.push import testing as push_testing
from pcapi.notifications.sms import testing as sms_testing
from pcapi.repository import repository
from pcapi.routes.native.v1.serialization import account as account_serializers

import tests
from tests.conftest import TestClient
from tests.connectors import user_profiling_fixtures

from .utils import create_user_and_test_client


pytestmark = pytest.mark.usefixtures("db_session")


class AccountTest:
    identifier = "email@example.com"

    def test_get_user_profile_without_authentication(self, app):
        users_factories.UserFactory(email=self.identifier)

        response = TestClient(app.test_client()).get("/native/v1/me")

        assert response.status_code == 401

    def test_get_user_profile_not_found(self, app):
        users_factories.UserFactory(email=self.identifier)

        access_token = create_access_token(identity="other-email@example.com")
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.get("/native/v1/me")

        assert response.status_code == 403
        assert response.json["email"] == ["Utilisateur introuvable"]

    def test_get_user_profile_not_active(self, app):
        users_factories.UserFactory(email=self.identifier, isActive=False)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.get("/native/v1/me")

        assert response.status_code == 403
        assert response.json["email"] == ["Utilisateur introuvable"]

    @freeze_time("2018-06-01")
    def test_get_user_profile(self, app):
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
            departementCode="93",
            **USER_DATA,
        )
        subscription_factories.SubscriptionMessageFactory(user=user)
        subscription_message = subscription_factories.SubscriptionMessageFactory(user=user, dateCreated=datetime.now())
        booking = IndividualBookingFactory(individualBooking__user=user, amount=Decimal("123.45"))
        CancelledIndividualBookingFactory(individualBooking__user=user, amount=Decimal("123.45"))

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.get("/native/v1/me")

        EXPECTED_DATA = {
            "allowedEligibilityCheckMethods": ["jouve"],
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
            "eligibilityEndDatetime": "2019-01-01T00:00:00Z",
            "eligibilityStartDatetime": "2015-01-01T00:00:00Z",
            "isBeneficiary": True,
            "roles": ["BENEFICIARY"],
            "hasCompletedIdCheck": None,
            "nextBeneficiaryValidationStep": None,
            "pseudo": "jdo",
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

    def test_get_user_not_beneficiary(self, app):
        users_factories.UserFactory(email=self.identifier)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.get("/native/v1/me")

        assert response.status_code == 200
        assert not response.json["domainsCredit"]

    def test_get_user_profile_empty_first_name(self, app):
        users_factories.UserFactory(email=self.identifier, firstName="", publicName=VOID_PUBLIC_NAME)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.get("/native/v1/me")

        assert response.status_code == 200
        assert response.json["email"] == self.identifier
        assert response.json["firstName"] is None
        assert response.json["pseudo"] is None
        assert not response.json["isBeneficiary"]
        assert response.json["roles"] == []

    def test_has_completed_id_check(self, app):
        user = users_factories.UserFactory(email=self.identifier)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/account/has_completed_id_check")

        assert response.status_code == 204

        db.session.refresh(user)
        assert user.hasCompletedIdCheck

        # One call should be sent to batch, and one to sendinblue
        assert len(push_testing.requests) == 1
        assert len(users_testing.sendinblue_requests) == 1

        sendinblue_data = users_testing.sendinblue_requests[0]
        assert sendinblue_data["attributes"]["HAS_COMPLETED_ID_CHECK"]

        me_response = test_client.get("/native/v1/me")
        assert me_response.json["hasCompletedIdCheck"]

    @pytest.mark.parametrize(
        "client_version,extra_step", [("1.154.9", "id-check"), ("1.160.0", "beneficiary-information")]
    )
    def test_next_beneficiary_validation_step(self, client_version, extra_step, client):
        user = users_factories.UserFactory(
            email=self.identifier, dateOfBirth=datetime.now() - relativedelta(years=18, days=5)
        )
        client.with_token(user.email)
        headers = {"app-version": client_version}

        response = client.get("/native/v1/me", headers=headers)

        assert response.json["nextBeneficiaryValidationStep"] == "phone-validation"
        assert response.status_code == 200

        # Perform phone validation and user profiling
        user.phoneValidationStatus = PhoneValidationStatusType.VALIDATED
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent=fraud_factories.UserProfilingFraudDataFactory(
                risk_rating=fraud_models.UserProfilingRiskRating.TRUSTED
            ),
        )

        response = client.get("/native/v1/me", headers=headers)

        assert response.status_code == 200
        assert response.json["nextBeneficiaryValidationStep"] == "id-check"

        # Perform ID card upload
        user.extraData["is_identity_document_uploaded"] = True
        repository.save(user)

        response = client.get("/native/v1/me", headers=headers)

        assert response.status_code == 200
        assert response.json["nextBeneficiaryValidationStep"] == extra_step
        print(headers, extra_step)

        # Perform final step
        user.add_beneficiary_role()

        response = client.get("/native/v1/me", headers=headers)

        assert response.status_code == 200
        assert not response.json["nextBeneficiaryValidationStep"]

    def test_next_beneficiary_validation_step_user_profiling_risk_rating_high(self, client):
        user = users_factories.UserFactory(
            email=self.identifier,
            dateOfBirth=datetime.now() - relativedelta(years=18, days=5),
        )
        client.with_token(user.email)

        # Perform phone validation and user profiling
        user.phoneValidationStatus = PhoneValidationStatusType.VALIDATED
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent=fraud_factories.UserProfilingFraudDataFactory(
                risk_rating=fraud_models.UserProfilingRiskRating.HIGH
            ),
        )

        response = client.get("/native/v1/me")
        assert response.status_code == 200
        assert response.json["nextBeneficiaryValidationStep"] == None

    @override_features(ALLOW_EMPTY_USER_PROFILING=False)
    def test_next_beneficiary_validation_step_no_user_profiling(self, client):
        user = users_factories.UserFactory(
            email=self.identifier,
            dateOfBirth=datetime.now() - relativedelta(years=18, days=5),
        )
        client.with_token(user.email)

        # Perform phone validation but no user profiling
        user.phoneValidationStatus = PhoneValidationStatusType.VALIDATED

        response = client.get("/native/v1/me")

        assert response.status_code == 200
        assert response.json["nextBeneficiaryValidationStep"] == None

    @override_features(ALLOW_EMPTY_USER_PROFILING=True)
    def test_next_beneficiary_validation_step_no_user_profiling_bypass(self, client):
        user = users_factories.UserFactory(
            email=self.identifier,
            dateOfBirth=datetime.now() - relativedelta(years=18, days=5),
        )
        client.with_token(user.email)

        # Perform phone validation but no user profiling
        user.phoneValidationStatus = PhoneValidationStatusType.VALIDATED

        response = client.get("/native/v1/me")

        assert response.status_code == 200
        assert response.json["nextBeneficiaryValidationStep"] == "id-check"

    @freeze_time("2021-06-01")
    def test_next_beneficiary_validation_step_not_eligible(self, app):
        users_factories.UserFactory(email=self.identifier, dateOfBirth=datetime(2000, 1, 1))

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.get("/native/v1/me")

        assert response.status_code == 200
        assert not response.json["nextBeneficiaryValidationStep"]

    @freeze_time("2021-06-01")
    def test_next_beneficiary_validation_step_underage(self, client):
        users_factories.UserFactory(email=self.identifier, dateOfBirth=datetime(2006, 1, 1))

        access_token = create_access_token(identity=self.identifier)
        client.auth_header = {"Authorization": f"Bearer {access_token}"}

        with override_features(ALLOW_IDCHECK_UNDERAGE_REGISTRATION=True, ENABLE_EDUCONNECT_AUTHENTICATION=False):
            response = client.get("/native/v1/me")
            assert response.status_code == 200
            assert response.json["allowedEligibilityCheckMethods"] == ["jouve"]
            assert response.json["nextBeneficiaryValidationStep"] == "id-check"

        with override_features(ALLOW_IDCHECK_UNDERAGE_REGISTRATION=False, ENABLE_EDUCONNECT_AUTHENTICATION=True):
            response = client.get("/native/v1/me")
            assert response.status_code == 200
            assert response.json["allowedEligibilityCheckMethods"] == ["educonnect"]
            assert response.json["nextBeneficiaryValidationStep"] == "id-check"

        with override_features(ALLOW_IDCHECK_UNDERAGE_REGISTRATION=True, ENABLE_EDUCONNECT_AUTHENTICATION=True):
            response = client.get("/native/v1/me")
            assert response.status_code == 200
            assert response.json["allowedEligibilityCheckMethods"] == ["educonnect", "jouve"]
            assert response.json["nextBeneficiaryValidationStep"] == "id-check"

        response = client.get("/native/v1/me")
        assert response.status_code == 200
        assert not response.json["allowedEligibilityCheckMethods"]
        assert not response.json["nextBeneficiaryValidationStep"]

    @freeze_time("2021-06-01")
    def test_next_beneficiary_validation_step_underage_not_eligible(self, client):
        users_factories.UserFactory(email=self.identifier, dateOfBirth=datetime(2006, 1, 1))

        access_token = create_access_token(identity=self.identifier)
        client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = client.get("/native/v1/me")
        assert response.status_code == 200
        assert not response.json["allowedEligibilityCheckMethods"]
        assert not response.json["nextBeneficiaryValidationStep"]

    def test_user_messages_passes_pydantic_serialization(self, client):
        user = users_factories.UserFactory()
        client.with_token(user.email)

        subscription_messages.create_message_jouve_manual_review(user, 1)
        response = client.get("/native/v1/me")
        assert response.status_code == 200

        subscription_messages.on_fraud_review_ko(user)
        response = client.get("/native/v1/me")
        assert response.status_code == 200

        subscription_messages.on_redirect_to_dms_from_idcheck(user)
        response = client.get("/native/v1/me")
        assert response.status_code == 200

        subscription_messages.on_idcheck_invalid_age(user)
        response = client.get("/native/v1/me")
        assert response.status_code == 200

        subscription_messages.on_idcheck_invalid_document(user)
        response = client.get("/native/v1/me")
        assert response.status_code == 200

        subscription_messages.on_idcheck_invalid_document_date(user)
        response = client.get("/native/v1/me")
        assert response.status_code == 200

        subscription_messages.on_idcheck_unread_mrz(user)
        response = client.get("/native/v1/me")
        assert response.status_code == 200

        subscription_messages.on_id_check_unread_document(user)
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


def build_test_client(app, identity):
    access_token = create_access_token(identity=identity)
    test_client = TestClient(app.test_client())
    test_client.auth_header = {"Authorization": f"Bearer {access_token}"}
    return test_client


class AccountCreationTest:
    identifier = "email@example.com"

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_account_creation(self, mocked_check_recaptcha_token_is_valid, app):
        test_client = TestClient(app.test_client())
        assert User.query.first() is None
        data = {
            "email": "John.doe@example.com",
            "password": "Aazflrifaoi6@",
            "birthdate": "1960-12-31",
            "notifications": True,
            "token": "gnagna",
            "marketingEmailSubscription": True,
        }

        response = test_client.post("/native/v1/account", json=data)
        assert response.status_code == 204, response.json

        user = User.query.first()
        assert user is not None
        assert user.email == "john.doe@example.com"
        assert user.get_notification_subscriptions().marketing_email
        assert user.isEmailValidated is False
        mocked_check_recaptcha_token_is_valid.assert_called()
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 2015423
        assert len(push_testing.requests) == 1
        assert len(users_testing.sendinblue_requests) == 1

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_account_creation_with_existing_email_sends_email(self, mocked_check_recaptcha_token_is_valid, app):
        test_client = TestClient(app.test_client())
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

        response = test_client.post("/native/v1/account", json=data)
        assert response.status_code == 204, response.json
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 1838526
        assert push_testing.requests == []

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_account_creation_with_unvalidated_email_sends_email(self, mocked_check_recaptcha_token_is_valid, app):
        test_client = TestClient(app.test_client())
        subscriber = users_factories.UserFactory(email=self.identifier, isEmailValidated=False)
        previous_token = users_factories.EmailValidationToken(user=subscriber).value
        mocked_check_recaptcha_token_is_valid.return_value = None

        data = {
            "email": "eMail@example.com",
            "password": "Aazflrifaoi6@",
            "birthdate": "1960-12-31",
            "notifications": True,
            "token": "some-token",
            "marketingEmailSubscription": True,
        }

        response = test_client.post("/native/v1/account", json=data)
        assert response.status_code == 204, response.json
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 2015423
        assert len(push_testing.requests) == 1
        subscriber.checkPassword(data["password"])

        tokens = Token.query.all()
        assert len(tokens) == 1
        assert previous_token != tokens[0].value

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_too_young_account_creation(self, mocked_check_recaptcha_token_is_valid, app):
        test_client = TestClient(app.test_client())
        assert User.query.first() is None
        data = {
            "email": "John.doe@example.com",
            "password": "Aazflrifaoi6@",
            "birthdate": (datetime.utcnow() - relativedelta(year=15)).date(),
            "notifications": True,
            "token": "gnagna",
            "marketingEmailSubscription": True,
        }

        response = test_client.post("/native/v1/account", json=data)
        assert response.status_code == 400
        assert push_testing.requests == []


class UserProfileUpdateTest:
    identifier = "email@example.com"

    def test_update_user_profile(self, app):
        users_factories.UserFactory(email=self.identifier)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post(
            "/native/v1/profile", json={"subscriptions": {"marketingPush": True, "marketingEmail": False}}
        )

        assert response.status_code == 200

        user = User.query.filter_by(email=self.identifier).first()
        assert user.get_notification_subscriptions().marketing_push
        assert not user.get_notification_subscriptions().marketing_email

        assert len(push_testing.requests) == 1

    def test_unsubscribe_push_notifications(self, app):
        user = users_factories.UserFactory(email=self.identifier)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post(
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
    def test_unsubscribe_push_notifications_with_batch(self, app, cloud_task_client):
        user = users_factories.UserFactory(email=self.identifier)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post(
            "/native/v1/profile", json={"subscriptions": {"marketingPush": False, "marketingEmail": False}}
        )

        assert response.status_code == 200
        assert cloud_task_client.create_task.call_count == 2

        ((_, ios_call_args), (_, android_call_args)) = cloud_task_client.create_task.call_args_list
        assert ios_call_args["request"]["task"]["http_request"] == {
            "body": b"null",
            "headers": {"Content-Type": "application/json", "X-Authorization": "coucou-la-cle"},
            "http_method": tasks_v2.HttpMethod.DELETE,
            "url": f"https://api.example.com/1.0/fake_ios_api_key/data/users/{user.id}",
        }

        assert android_call_args["request"]["task"]["http_request"] == {
            "body": b"null",
            "headers": {"Content-Type": "application/json", "X-Authorization": "coucou-la-cle"},
            "http_method": tasks_v2.HttpMethod.DELETE,
            "url": f"https://api.example.com/1.0/fake_android_api_key/data/users/{user.id}",
        }


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
    def test_resend_email_validation(self, app):
        user = users_factories.UserFactory(isEmailValidated=False)

        test_client = TestClient(app.test_client())
        response = test_client.post("/native/v1/resend_email_validation", json={"email": user.email})

        assert response.status_code == 204
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 2015423

    def test_for_already_validated_email_does_sent_passsword_reset(self, app):
        user = users_factories.UserFactory(isEmailValidated=True)

        test_client = TestClient(app.test_client())
        response = test_client.post("/native/v1/resend_email_validation", json={"email": user.email})

        assert response.status_code == 204
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 1838526

    def test_for_unknown_mail_does_nothing(self, app):
        test_client = TestClient(app.test_client())
        response = test_client.post("/native/v1/resend_email_validation", json={"email": "aijfioern@mlks.com"})

        assert response.status_code == 204
        assert not mails_testing.outbox

    def test_for_deactivated_account_does_nothhing(self, app):
        user = users_factories.UserFactory(isEmailValidated=True, isActive=False)

        test_client = TestClient(app.test_client())
        response = test_client.post("/native/v1/resend_email_validation", json={"email": user.email})

        assert response.status_code == 204
        assert not mails_testing.outbox


@freeze_time("2018-06-01")
class GetIdCheckTokenTest:
    def test_get_id_check_token_eligible(self, app):
        user = users_factories.UserFactory(dateOfBirth=datetime(2000, 1, 1), departementCode="93")
        access_token = create_access_token(identity=user.email)

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}
        response = test_client.get("/native/v1/id_check_token")

        assert response.status_code == 200
        assert get_id_check_token(response.json["token"])

    def test_get_id_check_token_not_eligible(self, app):
        user = users_factories.UserFactory(dateOfBirth=datetime(2001, 1, 1), departementCode="984")
        access_token = create_access_token(identity=user.email)

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}
        response = test_client.get("/native/v1/id_check_token")

        assert response.status_code == 400
        assert response.json == {"code": "USER_NOT_ELIGIBLE"}

    def test_get_id_check_token_limit_reached(self, app):
        user = users_factories.UserFactory(dateOfBirth=datetime(2000, 1, 1), departementCode="93")

        expiration_date = datetime.now() + timedelta(hours=2)
        users_factories.IdCheckToken.create_batch(
            settings.ID_CHECK_MAX_ALIVE_TOKEN, user=user, expirationDate=expiration_date, isUsed=False
        )

        access_token = create_access_token(identity=user.email)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}
        response = test_client.get("/native/v1/id_check_token")

        assert response.status_code == 400
        assert response.json["code"] == "TOO_MANY_ID_CHECK_TOKEN"


@freeze_time("2018-06-01")
class UploadIdentityDocumentTest:
    IMAGES_DIR = Path(tests.__path__[0]) / "files"

    @patch("pcapi.core.users.api.verify_identity_document")
    @patch("pcapi.core.users.api.store_object")
    @patch("pcapi.core.users.api.random_token")
    def test_upload_identity_document_successful(
        self,
        mocked_random_token,
        mocked_store_object,
        mocked_verify_identity_document,
        app,
    ):
        user = users_factories.UserFactory(dateOfBirth=datetime(2000, 1, 1), departementCode="93")
        token = TokenFactory(user=user, type=TokenType.ID_CHECK)
        access_token = create_access_token(identity=user.email)
        mocked_random_token.return_value = "a_very_random_secret"

        identity_document = (self.IMAGES_DIR / "mouette_small.jpg").read_bytes()
        data = {
            "identityDocumentFile": (BytesIO(identity_document), "image.jpg"),
            "token": token.value,
        }

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}
        response = test_client.post("/native/v1/identity_document", form=data)

        assert response.status_code == 204
        mocked_store_object.assert_called_once_with(
            "identity_documents",
            "a_very_random_secret.jpg",
            identity_document,
            content_type="image/jpeg",
            metadata={"email": user.email},
        )
        mocked_verify_identity_document.delay.assert_called_once_with(
            {"image_storage_path": "identity_documents/a_very_random_secret.jpg"}
        )

    def test_ineligible_user(self, app):
        user = users_factories.UserFactory(dateOfBirth=datetime(2000, 1, 1), departementCode="984")
        access_token = create_access_token(identity=user.email)
        token = TokenFactory(user=user, type=TokenType.ID_CHECK)

        thumb = (self.IMAGES_DIR / "pixel.png").read_bytes()
        data = {"identityDocumentFile": (BytesIO(thumb), "image.jpg"), "token": token.value}

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}
        response = test_client.post("/native/v1/identity_document", form=data)

        assert response.status_code == 400
        assert response.json == {"code": "USER_NOT_ELIGIBLE"}

    def test_token_expired(self, app):
        user = users_factories.UserFactory(dateOfBirth=datetime(2000, 1, 1), departementCode="93")
        access_token = create_access_token(identity=user.email)
        token = TokenFactory(user=user, type=TokenType.ID_CHECK, expirationDate=datetime(2000, 1, 1))

        thumb = (self.IMAGES_DIR / "pixel.png").read_bytes()
        data = {"identityDocumentFile": (BytesIO(thumb), "image.jpg"), "token": token.value}

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}
        response = test_client.post("/native/v1/identity_document", form=data)

        assert response.status_code == 400
        assert response.json == {"code": "EXPIRED_TOKEN", "message": "Token expiré"}

    def test_token_used(self, app):
        user = users_factories.UserFactory(dateOfBirth=datetime(2000, 1, 1), departementCode="93")
        token = TokenFactory(user=user, type=TokenType.ID_CHECK, isUsed=True)

        thumb = (self.IMAGES_DIR / "pixel.png").read_bytes()
        data = {
            "identityDocumentFile": (BytesIO(thumb), "image.jpg"),
            "token": token.value,
        }

        access_token = create_access_token(identity=user.email)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}
        response = test_client.post("/native/v1/identity_document", form=data)

        assert response.status_code == 400
        assert response.json["code"] == "EXPIRED_TOKEN"

    def test_no_token_found(self, app):
        user = users_factories.UserFactory(dateOfBirth=datetime(2000, 1, 1), departementCode="93")
        token = TokenFactory(user=user, type=TokenType.ID_CHECK, isUsed=True)

        thumb = (self.IMAGES_DIR / "pixel.png").read_bytes()
        data = {
            "identityDocumentFile": (BytesIO(thumb), "image.jpg"),
            "token": f"{token.value}wrongsuffix",
        }

        access_token = create_access_token(identity=user.email)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}
        response = test_client.post("/native/v1/identity_document", form=data)

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_TOKEN"


class ShowEligibleCardTest:
    @pytest.mark.parametrize("age,expected", [(17, False), (18, True), (19, False)])
    def test_against_different_age(self, age, expected):
        date_of_birth = datetime.now() - relativedelta(years=age, days=5)
        date_of_creation = datetime.now() - relativedelta(years=4)
        user = users_factories.UserFactory.build(
            dateOfBirth=date_of_birth, dateCreated=date_of_creation, departementCode="93"
        )
        assert account_serializers.UserProfileResponse._show_eligible_card(user) == expected

    @pytest.mark.parametrize("beneficiary,expected", [(False, True), (True, False)])
    def test_against_beneficiary(self, beneficiary, expected):
        date_of_birth = datetime.now() - relativedelta(years=18, days=5)
        date_of_creation = datetime.now() - relativedelta(years=4)
        roles = [UserRole.BENEFICIARY] if beneficiary else []
        user = users_factories.UserFactory.build(
            dateOfBirth=date_of_birth,
            dateCreated=date_of_creation,
            departementCode="93",
            roles=roles,
        )
        assert account_serializers.UserProfileResponse._show_eligible_card(user) == expected

    def test_user_eligible_but_created_after_18(self):
        date_of_birth = datetime.now() - relativedelta(years=18, days=5)
        date_of_creation = datetime.now()
        user = users_factories.UserFactory.build(dateOfBirth=date_of_birth, dateCreated=date_of_creation)
        assert account_serializers.UserProfileResponse._show_eligible_card(user) == False


class SendPhoneValidationCodeTest:
    def test_send_phone_validation_code(self, app):
        user = users_factories.UserFactory(departementCode="93", phoneNumber="+33601020304")
        access_token = create_access_token(identity=user.email)

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/send_phone_validation_code")

        assert response.status_code == 204

        assert int(app.redis_client.get(f"sent_SMS_counter_user_{user.id}")) == 1

        token = Token.query.filter_by(userId=user.id, type=TokenType.PHONE_VALIDATION).first()

        assert token.expirationDate >= datetime.now() + timedelta(minutes=2)
        assert token.expirationDate < datetime.now() + timedelta(minutes=30)

        assert sms_testing.requests == [
            {"recipient": "+33601020304", "content": f"{token.value} est ton code de confirmation pass Culture"}
        ]
        assert len(token.value) == 6
        assert 0 <= int(token.value) < 1000000

        # validate phone number with generated code
        response = test_client.post("/native/v1/validate_phone_number", json={"code": token.value})

        assert response.status_code == 204
        user = User.query.get(user.id)
        assert user.is_phone_validated

    @override_settings(MAX_SMS_SENT_FOR_PHONE_VALIDATION=1)
    def test_send_phone_validation_code_too_many_attempts(self, app):
        user = users_factories.UserFactory(departementCode="93", phoneNumber="+33601020304")
        access_token = create_access_token(identity=user.email)

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/send_phone_validation_code")
        assert response.status_code == 204

        response = test_client.post("/native/v1/send_phone_validation_code")
        assert response.status_code == 400
        assert response.json["code"] == "TOO_MANY_SMS_SENT"

        # check that a fraud check has been created
        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            userId=user.id, type=fraud_models.FraudCheckType.INTERNAL_REVIEW, thirdPartyId=f"PC-{user.id}"
        ).one_or_none()

        assert fraud_check is not None

        content = fraud_check.resultContent
        expected_reason = "Le nombre maximum de sms envoyés est atteint"
        assert content["source"] == fraud_models.InternalReviewSource.SMS_SENDING_LIMIT_REACHED.value
        assert content["message"] == expected_reason
        assert content["phone_number"] == "+33601020304"

        # check that a fraud result has also been created
        assert user.beneficiaryFraudResult
        assert user.beneficiaryFraudResult.status == fraud_models.FraudStatus.SUSPICIOUS
        assert user.beneficiaryFraudResult.reason == expected_reason

    def test_send_phone_validation_code_already_beneficiary(self, app):
        user = users_factories.BeneficiaryGrant18Factory(
            isEmailValidated=True, phoneNumber="+33601020304", roles=[UserRole.BENEFICIARY]
        )
        access_token = create_access_token(identity=user.email)

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/send_phone_validation_code")

        assert response.status_code == 400

        assert not Token.query.filter_by(userId=user.id).first()

    def test_send_phone_validation_code_for_new_phone_with_already_beneficiary(self, app):
        user = users_factories.BeneficiaryGrant18Factory(
            isEmailValidated=True, phoneNumber="+33601020304", roles=[UserRole.BENEFICIARY]
        )
        access_token = create_access_token(identity=user.email)

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33102030405"})

        assert response.status_code == 400

        assert not Token.query.filter_by(userId=user.id).first()
        db.session.refresh(user)
        assert user.phoneNumber == "+33601020304"

    def test_send_phone_validation_code_for_new_phone_updates_phone(self, app):
        user = users_factories.UserFactory(isEmailValidated=True, phoneNumber="+33601020304")
        access_token = create_access_token(identity=user.email)

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33102030405"})

        assert response.status_code == 204

        assert Token.query.filter_by(userId=user.id).first()
        db.session.refresh(user)
        assert user.phoneNumber == "+33102030405"

    def test_send_phone_validation_code_for_new_unvalidated_duplicated_phone_number(self, app):
        users_factories.UserFactory(isEmailValidated=True, phoneNumber="+33102030405")
        user = users_factories.UserFactory(isEmailValidated=True, phoneNumber="+33601020304")
        access_token = create_access_token(identity=user.email)

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33102030405"})

        assert response.status_code == 204

        db.session.refresh(user)
        assert user.phoneNumber == "+33102030405"

    def test_send_phone_validation_code_for_new_validated_duplicated_phone_number(self, app):
        orig_user = users_factories.UserFactory(
            isEmailValidated=True,
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
            phoneNumber="+33102030405",
        )
        user = users_factories.UserFactory(isEmailValidated=True, phoneNumber="+33601020304")
        access_token = create_access_token(identity=user.email)

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33102030405"})

        assert response.status_code == 400

        assert not Token.query.filter_by(userId=user.id).first()
        db.session.refresh(user)
        assert user.phoneNumber == "+33601020304"
        assert response.json == {"message": "Le numéro de téléphone est invalide", "code": "INVALID_PHONE_NUMBER"}

        # check that a fraud check has been created
        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            userId=user.id, type=fraud_models.FraudCheckType.INTERNAL_REVIEW, thirdPartyId=f"PC-{user.id}"
        ).one_or_none()

        assert fraud_check is not None

        content = fraud_check.resultContent
        assert content["source"] == fraud_models.InternalReviewSource.PHONE_ALREADY_EXISTS.value
        assert content["message"] == f"Le numéro est déjà utilisé par l'utilisateur {orig_user.id}"
        assert content["phone_number"] == "+33102030405"

    @override_settings(BLACKLISTED_SMS_RECIPIENTS={"+33607080900"})
    def test_update_phone_number_with_blocked_phone_number(self, app):
        user = users_factories.UserFactory(isEmailValidated=True, phoneNumber="+33601020304")
        access_token = create_access_token(identity=user.email)

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33607080900"})

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_PHONE_NUMBER"

        assert not Token.query.filter_by(userId=user.id).first()
        db.session.refresh(user)
        assert user.phoneNumber == "+33601020304"

    def test_send_phone_validation_code_with_malformed_number(self, app):
        # user's phone number should be in international format (E.164): +33601020304
        user = users_factories.UserFactory(isEmailValidated=True, phoneNumber="0601020304")
        access_token = create_access_token(identity=user.email)

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/send_phone_validation_code")

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_PHONE_NUMBER"
        assert not Token.query.filter_by(userId=user.id).first()

    def test_send_phone_validation_code_with_non_french_number(self, app):
        user = users_factories.UserFactory(isEmailValidated=True, phoneNumber="+46766123456")
        access_token = create_access_token(identity=user.email)

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/send_phone_validation_code")

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_PHONE_NUMBER"
        assert not Token.query.filter_by(userId=user.id).first()

    def test_update_phone_number_with_non_french_number(self, app):
        user = users_factories.UserFactory(isEmailValidated=True, phoneNumber="+46766123456")
        access_token = create_access_token(identity=user.email)

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+46766987654"})

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_PHONE_NUMBER"
        assert not Token.query.filter_by(userId=user.id).first()

        db.session.refresh(user)
        assert user.phoneNumber == "+46766123456"

    @override_settings(BLACKLISTED_SMS_RECIPIENTS={"+33601020304"})
    def test_blocked_phone_number(self, app):
        user = users_factories.UserFactory(departementCode="93", phoneNumber="+33601020304")
        access_token = create_access_token(identity=user.email)

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/send_phone_validation_code")

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_PHONE_NUMBER"

        assert not Token.query.filter_by(userId=user.id).first()
        db.session.refresh(user)
        assert user.phoneNumber == "+33601020304"

        # check that a fraud check has been created
        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            userId=user.id, type=fraud_models.FraudCheckType.INTERNAL_REVIEW, thirdPartyId=f"PC-{user.id}"
        ).one_or_none()

        assert fraud_check is not None

        content = fraud_check.resultContent
        assert content["source"] == fraud_models.InternalReviewSource.BLACKLISTED_PHONE_NUMBER.value
        assert content["message"] == "Le numéro saisi est interdit"
        assert content["phone_number"] == "+33601020304"


class ValidatePhoneNumberTest:
    def test_validate_phone_number(self, app):
        user = users_factories.UserFactory(phoneNumber="+33607080900")
        access_token = create_access_token(identity=user.email)
        token = create_phone_validation_token(user)

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        # try one attempt with wrong code
        test_client.post("/native/v1/validate_phone_number", {"code": "wrong code"})
        response = test_client.post("/native/v1/validate_phone_number", {"code": token.value})

        assert response.status_code == 204
        user = User.query.get(user.id)
        assert user.is_phone_validated
        assert not user.has_beneficiary_role

        token = Token.query.filter_by(userId=user.id, type=TokenType.PHONE_VALIDATION).first()

        assert not token

        assert int(app.redis_client.get(f"phone_validation_attempts_user_{user.id}")) == 2

    def test_validate_phone_number_and_become_beneficiary(self, app):
        user = users_factories.UserFactory(phoneNumber="+33607080900", hasCompletedIdCheck=True)

        beneficiary_import = BeneficiaryImportFactory(beneficiary=user)
        beneficiary_import.setStatus(ImportStatus.CREATED)

        access_token = create_access_token(identity=user.email)
        token = create_phone_validation_token(user)

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/validate_phone_number", {"code": token.value})

        assert response.status_code == 204
        user = User.query.get(user.id)
        assert user.is_phone_validated
        assert user.has_beneficiary_role

    @override_settings(MAX_PHONE_VALIDATION_ATTEMPTS=1)
    def test_validate_phone_number_too_many_attempts(self, app):
        user = users_factories.UserFactory(phoneNumber="+33607080900")
        access_token = create_access_token(identity=user.email)
        token = create_phone_validation_token(user)

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/validate_phone_number", {"code": "wrong code"})
        response = test_client.post("/native/v1/validate_phone_number", {"code": token.value})

        assert response.status_code == 400
        assert response.json["message"] == "Le nombre de tentatives maximal est dépassé"
        assert response.json["code"] == "TOO_MANY_VALIDATION_ATTEMPTS"

        db.session.refresh(user)
        assert not user.is_phone_validated

        attempts_count = int(app.redis_client.get(f"phone_validation_attempts_user_{user.id}"))
        assert attempts_count == 1

        # check that a fraud check has been created
        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            userId=user.id, type=fraud_models.FraudCheckType.INTERNAL_REVIEW, thirdPartyId=f"PC-{user.id}"
        ).one_or_none()

        assert fraud_check is not None

        expected_reason = f"Le nombre maximum de tentatives de validation est atteint: {attempts_count}"
        content = fraud_check.resultContent
        assert content["source"] == fraud_models.InternalReviewSource.PHONE_VALIDATION_ATTEMPTS_LIMIT_REACHED.value
        assert content["message"] == expected_reason
        assert content["phone_number"] == "+33607080900"

        # check that a fraud result has also been created
        assert user.beneficiaryFraudResult
        assert user.beneficiaryFraudResult.status == fraud_models.FraudStatus.SUSPICIOUS
        assert user.beneficiaryFraudResult.reason == expected_reason

    def test_wrong_code(self, app):
        user = users_factories.UserFactory(phoneNumber="+33607080900")
        access_token = create_access_token(identity=user.email)
        create_phone_validation_token(user)

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.post("/native/v1/validate_phone_number", {"code": "mauvais-code"})

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_VALIDATION_CODE"

        assert not User.query.get(user.id).is_phone_validated
        assert Token.query.filter_by(userId=user.id, type=TokenType.PHONE_VALIDATION).first()

    def test_expired_code(self, app):
        user = users_factories.UserFactory(phoneNumber="+33607080900")
        token = create_phone_validation_token(user)

        with freeze_time(datetime.now() + timedelta(minutes=20)):
            access_token = create_access_token(identity=user.email)
            test_client = TestClient(app.test_client())
            test_client.auth_header = {"Authorization": f"Bearer {access_token}"}
            response = test_client.post("/native/v1/validate_phone_number", {"code": token.value})

        assert response.status_code == 400
        assert response.json["code"] == "EXPIRED_VALIDATION_CODE"

        assert not User.query.get(user.id).is_phone_validated
        assert Token.query.filter_by(userId=user.id, type=TokenType.PHONE_VALIDATION).first()

    @override_settings(BLACKLISTED_SMS_RECIPIENTS={"+33607080900"})
    def test_blocked_phone_number(self, app):
        user = users_factories.UserFactory(phoneNumber="+33607080900")
        token = create_phone_validation_token(user)

        access_token = create_access_token(identity=user.email)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}
        response = test_client.post("/native/v1/validate_phone_number", {"code": token.value})

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_PHONE_NUMBER"

        assert not User.query.get(user.id).is_phone_validated
        assert Token.query.filter_by(userId=user.id, type=TokenType.PHONE_VALIDATION).first()

    def test_validate_phone_number_with_non_french_number(self, app):
        user = users_factories.UserFactory(phoneNumber="+46766123456")
        token = create_phone_validation_token(user)

        access_token = create_access_token(identity=user.email)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}
        response = test_client.post("/native/v1/validate_phone_number", {"code": token.value})

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_PHONE_NUMBER"

        assert not User.query.get(user.id).is_phone_validated
        assert Token.query.filter_by(userId=user.id, type=TokenType.PHONE_VALIDATION).first()

    def test_validate_phone_number_with_already_validated_phone(self, app):
        users_factories.UserFactory(
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED, phoneNumber="+33607080900"
        )
        user = users_factories.UserFactory(phoneNumber="+33607080900")
        access_token = create_access_token(identity=user.email)
        token = create_phone_validation_token(user)

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        # try one attempt with wrong code
        response = test_client.post("/native/v1/validate_phone_number", {"code": token.value})

        assert response.status_code == 400
        user = User.query.get(user.id)
        assert not user.is_phone_validated

        token = Token.query.filter_by(userId=user.id, type=TokenType.PHONE_VALIDATION).first()
        assert not token

        assert int(app.redis_client.get(f"phone_validation_attempts_user_{user.id}")) == 1


def test_suspend_account(app):
    booking = booking_factories.IndividualBookingFactory()
    user = booking.individualBooking.user

    access_token = create_access_token(identity=user.email)
    test_client = TestClient(app.test_client())
    test_client.auth_header = {"Authorization": f"Bearer {access_token}"}
    response = test_client.post("/native/v1/account/suspend")

    assert response.status_code == 204
    assert booking.isCancelled
    assert not user.isActive
    assert user.suspensionReason == SuspensionReason.UPON_USER_REQUEST.value


class UpdateBeneficiaryInformationTest:
    def test_update_beneficiary_information(self, app):
        """
        Test that valid request:
            * updates the user's id check profile information;
            * sets the user to beneficiary;
            * send a request to Batch to update the user's information
        """
        user = users_factories.UserFactory(
            address=None,
            city=None,
            postalCode=None,
            activity=None,
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
            phoneNumber="+33609080706",
        )
        fraud_factories.BeneficiaryFraudResultFactory(user=user, status=fraud_models.FraudStatus.OK)

        beneficiary_import = BeneficiaryImportFactory(beneficiary=user)
        beneficiary_import.setStatus(ImportStatus.CREATED)

        access_token = create_access_token(identity=user.email)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        profile_data = {
            "address": "1 rue des rues",
            "city": "Uneville",
            "postalCode": "77000",
            "activity": "Lycéen",
        }

        response = test_client.patch("/native/v1/beneficiary_information", profile_data)

        assert response.status_code == 204

        user = User.query.get(user.id)
        assert user.address == "1 rue des rues"
        assert user.city == "Uneville"
        assert user.postalCode == "77000"
        assert user.activity == "Lycéen"
        assert user.phoneNumber == "+33609080706"

        assert user.has_beneficiary_role
        assert user.deposit

        assert len(push_testing.requests) == 1
        notification = push_testing.requests[0]

        assert notification["user_id"] == user.id
        assert notification["attribute_values"]["u.is_beneficiary"]
        assert notification["attribute_values"]["u.postal_code"] == "77000"

    @override_features(ENABLE_PHONE_VALIDATION=False)
    def test_update_beneficiary_information_without_address(self, app):
        """
        Test that valid request:
            * updates the user's id check profile information;
            * sets the user to beneficiary;
            * send a request to Batch to update the user's information
        """
        user = users_factories.UserFactory(
            address=None,
            city=None,
            postalCode=None,
            activity=None,
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
        )
        fraud_factories.BeneficiaryFraudResultFactory(user=user, status=fraud_models.FraudStatus.OK)

        beneficiary_import = BeneficiaryImportFactory(beneficiary=user)
        beneficiary_import.setStatus(ImportStatus.CREATED)

        access_token = create_access_token(identity=user.email)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        profile_data = {
            "address": None,
            "city": "Uneville",
            "postalCode": "77000",
            "activity": "Lycéen",
            "phone": "0601020304",
        }

        response = test_client.patch("/native/v1/beneficiary_information", profile_data)

        assert response.status_code == 204

        user = User.query.get(user.id)
        assert user.address is None
        assert user.city == "Uneville"
        assert user.postalCode == "77000"
        assert user.activity == "Lycéen"
        assert user.phoneNumber == "0601020304"

        assert user.has_beneficiary_role
        assert user.deposit

        assert len(push_testing.requests) == 1
        notification = push_testing.requests[0]

        assert notification["user_id"] == user.id
        assert notification["attribute_values"]["u.is_beneficiary"]
        assert notification["attribute_values"]["u.postal_code"] == "77000"

    @override_features(ENABLE_PHONE_VALIDATION=True)
    def test_update_beneficiary_phone_number_not_updated(self, app):
        """
        Test that valid request:
            * updates the user's id check profile information;
            * sets the user to beneficiary;
            * send a request to Batch to update the user's information
        """
        user = users_factories.UserFactory(
            address=None,
            city=None,
            postalCode=None,
            activity=None,
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
        )
        fraud_factories.BeneficiaryFraudResultFactory(user=user, status=fraud_models.FraudStatus.OK)

        beneficiary_import = BeneficiaryImportFactory(beneficiary=user)
        beneficiary_import.setStatus(ImportStatus.CREATED)

        access_token = create_access_token(identity=user.email)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        profile_data = {
            "address": None,
            "city": "Uneville",
            "postalCode": "77000",
            "activity": "Lycéen",
            "phone": "0601020304",
        }

        response = test_client.patch("/native/v1/beneficiary_information", profile_data)

        assert response.status_code == 204

        user = User.query.get(user.id)
        assert user.address is None
        assert user.city == "Uneville"
        assert user.postalCode == "77000"
        assert user.activity == "Lycéen"
        assert user.phoneNumber is None

        assert user.has_beneficiary_role
        assert user.deposit

        assert len(push_testing.requests) == 1

    @override_features(ENABLE_PHONE_VALIDATION=True)
    def test_update_beneficiary_underage(self, app):
        """
        Test that valid request:
            * updates the user's id check profile information;
            * sets the user to beneficiary;
            * send a request to Batch to update the user's information
        """
        user = users_factories.UserFactory(
            address=None,
            city=None,
            dateOfBirth=datetime.now() - relativedelta(years=15, months=4),
            postalCode=None,
            activity=None,
        )
        fraud_factories.BeneficiaryFraudResultFactory(user=user, status=fraud_models.FraudStatus.OK)

        beneficiary_import = BeneficiaryImportFactory(beneficiary=user, eligibilityType=EligibilityType.UNDERAGE)
        beneficiary_import.setStatus(ImportStatus.CREATED)

        access_token = create_access_token(identity=user.email)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        profile_data = {
            "address": None,
            "city": "Uneville",
            "postalCode": "77000",
            "activity": "Lycéen",
            "phone": "0601020304",
        }

        response = test_client.patch("/native/v1/beneficiary_information", profile_data)

        assert response.status_code == 204

        user = User.query.get(user.id)
        assert user.address is None
        assert user.city == "Uneville"
        assert user.postalCode == "77000"
        assert user.activity == "Lycéen"
        assert user.phoneNumber is None

        assert user.roles == [UserRole.UNDERAGE_BENEFICIARY]
        assert user.deposit.amount == 20

        assert len(push_testing.requests) == 1


class ProfilingFraudScoreTest:

    USER_PROFILING_URL = "https://example.com/path"

    @override_settings(USER_PROFILING_URL=USER_PROFILING_URL)
    def test_profiling_fraud_score_call(self, client, requests_mock):
        user = users_factories.UserFactory()
        session_id = "arbitrarysessionid"
        matcher = requests_mock.register_uri(
            "POST",
            settings.USER_PROFILING_URL,
            json=user_profiling_fixtures.CORRECT_RESPONSE,
            status_code=200,
        )
        client.with_token(user.email)

        response = client.post("/native/v1/user_profiling", json={"session_id": session_id})
        assert response.status_code == 204
        assert matcher.call_count == 1

    @override_settings(USER_PROFILING_URL=USER_PROFILING_URL)
    def test_profiling_fraud_score_call_error(self, client, requests_mock, caplog):
        user = users_factories.UserFactory()
        matcher = requests_mock.register_uri(
            "POST",
            settings.USER_PROFILING_URL,
            json=user_profiling_fixtures.PARAMETER_ERROR_RESPONSE,
            status_code=500,
        )
        client.with_token(user.email)
        response = client.post("/native/v1/user_profiling", json={"session_id": "randomsessionid"})
        assert response.status_code == 204
        assert matcher.call_count == 1
        assert caplog.record_tuples == [
            ("pcapi.routes.native.v1.account", 40, "Error while retrieving user profiling infos")
        ]

    @override_settings(USER_PROFILING_URL=USER_PROFILING_URL)
    def test_profiling_fraud_score_user_without_birth_date(self, client, requests_mock, caplog):
        user = users_factories.UserFactory(dateOfBirth=None)
        matcher = requests_mock.register_uri(
            "POST",
            settings.USER_PROFILING_URL,
            json=user_profiling_fixtures.CORRECT_RESPONSE,
            status_code=200,
        )
        client.with_token(user.email)

        with caplog.at_level(logging.INFO):
            response = client.post("/native/v1/user_profiling", json={"session_id": "randomsessionid"})
        assert response.status_code == 204
        assert matcher.call_count == 1
        assert len(caplog.records) >= 2
        assert caplog.record_tuples[0][-1] == "External service called"
        assert caplog.record_tuples[1][-1].startswith("Success when profiling user:")
        assert fraud_models.BeneficiaryFraudCheck.query.count() == 1
        fraud_check = fraud_models.BeneficiaryFraudCheck.query.first()
        assert fraud_check.userId == user.id
        assert fraud_check.type == fraud_models.FraudCheckType.USER_PROFILING

    @override_settings(USER_PROFILING_URL=USER_PROFILING_URL)
    def test_profiling_session_id_invalid(self, client, requests_mock):
        user = users_factories.UserFactory()
        matcher = requests_mock.register_uri(
            "POST",
            settings.USER_PROFILING_URL,
            json=user_profiling_fixtures.CORRECT_RESPONSE,
            status_code=200,
        )
        client.with_token(user.email)
        response = client.post("/native/v1/user_profiling", json={"session_id": "gdavmoioeuboaobç!p'è"})
        assert response.status_code == 400
        assert matcher.call_count == 0

    @override_settings(USER_PROFILING_URL=USER_PROFILING_URL)
    @pytest.mark.parametrize(
        "risk_rating",
        (
            fraud_models.UserProfilingRiskRating.HIGH,
            fraud_models.UserProfilingRiskRating.MEDIUM,
        ),
    )
    def test_fraud_result_on_risky_user_profiling(self, client, requests_mock, risk_rating):
        user = users_factories.UserFactory()
        session_id = "arbitrarysessionid"
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

        response = client.post("/native/v1/user_profiling", json={"session_id": session_id})

        assert response.status_code == 204
        assert (
            fraud_models.BeneficiaryFraudResult.query.filter(fraud_models.BeneficiaryFraudResult.user == user).count()
            == 1
        )
        assert len(user.subscriptionMessages) == 1
        sub_message = user.subscriptionMessages[0]
        assert sub_message.userMessage == "Ton inscription n'a pas pu aboutir."

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
        user = users_factories.UserFactory()
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
        session_id = "arbitrarysessionid"

        response = client.post("/native/v1/user_profiling", json={"session_id": session_id})

        assert response.status_code == 204
        assert (
            fraud_models.BeneficiaryFraudResult.query.filter(fraud_models.BeneficiaryFraudResult.user == user).count()
            == 0
        )


class IdentificationSessionTest:
    def test_request(self, client, ubble_mock):
        user = users_factories.UserFactory()

        client.with_token(user.email)

        response = client.post("/native/v1/ubble_identification", json={"redirect_url": "http://example.com/deeplink"})

        assert response.status_code == 200
        assert len(user.beneficiaryFraudChecks) == 1
        assert ubble_mock.call_count == 1

        check = user.beneficiaryFraudChecks[0]
        assert check.type == fraud_models.FraudCheckType.UBBLE
