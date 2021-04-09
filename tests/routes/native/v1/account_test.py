from datetime import datetime
from decimal import Decimal
from unittest.mock import patch
import uuid

from dateutil.relativedelta import relativedelta
from flask_jwt_extended.utils import create_access_token
from freezegun.api import freeze_time
import pytest

from pcapi.core.bookings.factories import BookingFactory
import pcapi.core.mails.testing as mails_testing
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users.models import User
from pcapi.core.users.models import VOID_PUBLIC_NAME
from pcapi.core.users.repository import get_id_check_token
from pcapi.notifications.push import testing as push_testing
from pcapi.routes.native.v1.serialization import account as account_serializers

from tests.conftest import TestClient

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
            "phoneNumber": "0102030405",
            "needsToFillCulturalSurvey": True,
        }
        user = users_factories.UserFactory(
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
        booking = BookingFactory(user=user, amount=Decimal("123.45"))
        BookingFactory(user=user, amount=Decimal("123.45"), isCancelled=True)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.get("/native/v1/me")

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
            "depositExpirationDate": "2040-01-01T00:00:00Z",
            "eligibilityEndDatetime": "2019-01-01T00:00:00Z",
            "eligibilityStartDatetime": "2018-01-01T00:00:00Z",
            "expenses": [
                {"current": 12345, "domain": "all", "limit": 50000},
                {"current": 0, "domain": "digital", "limit": 20000},
                {"current": 12345, "domain": "physical", "limit": 20000},
            ],
            "isBeneficiary": True,
            "pseudo": "jdo",
            "showEligibleCard": False,
            "subscriptions": {"marketingPush": True, "marketingEmail": True},
        }
        EXPECTED_DATA.update(USER_DATA)

        assert response.status_code == 200
        assert response.json == EXPECTED_DATA

    @override_features(WHOLE_FRANCE_OPENING=False)
    @freeze_time("2018-06-01")
    def test_get_user_profile_from_non_eligible_area(self, app):
        USER_DATA = {
            "email": self.identifier,
            "firstName": "john",
            "lastName": "doe",
            "phoneNumber": "0102030405",
            "needsToFillCulturalSurvey": True,
        }
        user = users_factories.UserFactory(
            dateOfBirth=datetime(2000, 1, 1),
            deposit__version=1,
            # The expiration date is taken in account in
            # `get_wallet_balance` and compared against the SQL
            # `now()` function, which is NOT overriden by
            # `freeze_time()`.
            deposit__expirationDate=datetime(2040, 1, 1),
            notificationSubscriptions={"marketing_push": True},
            publicName="jdo",
            departementCode="92",
            isBeneficiary=False,
            **USER_DATA,
        )

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.get("/native/v1/me")

        EXPECTED_DATA = {
            "id": user.id,
            "bookedOffers": {},
            "domainsCredit": None,
            "dateOfBirth": "2000-01-01",
            "depositVersion": None,
            "depositExpirationDate": None,
            "eligibilityEndDatetime": None,
            "eligibilityStartDatetime": None,
            "expenses": [],
            "isBeneficiary": False,
            "pseudo": "jdo",
            "showEligibleCard": False,
            "subscriptions": {"marketingPush": True, "marketingEmail": True},
        }
        EXPECTED_DATA.update(USER_DATA)

        assert response.status_code == 200
        assert response.json == EXPECTED_DATA

    def test_get_user_not_beneficiary(self, app):
        users_factories.UserFactory(email=self.identifier, deposit=None, isBeneficiary=False)

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.get("/native/v1/me")

        assert response.status_code == 200
        assert not response.json["domainsCredit"]

    def test_get_user_profile_empty_first_name(self, app):
        users_factories.UserFactory(
            email=self.identifier, firstName="", isBeneficiary=False, publicName=VOID_PUBLIC_NAME
        )

        access_token = create_access_token(identity=self.identifier)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

        response = test_client.get("/native/v1/me")

        assert response.status_code == 200
        assert response.json["email"] == self.identifier
        assert response.json["firstName"] is None
        assert response.json["pseudo"] is None
        assert not response.json["isBeneficiary"]

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
        assert push_testing.requests == [
            {
                "attribute_values": {
                    "date(u.date_created)": user.dateCreated.strftime("%Y-%m-%dT%H:%M:%S"),
                    "date(u.date_of_birth)": "1960-12-31T00:00:00",
                    "date(u.deposit_expiration_date)": None,
                    "u.credit": 0,
                    "u.is_beneficiary": False,
                    "u.marketing_push_subscription": True,
                    "u.postal_code": None,
                },
                "user_id": user.id,
            }
        ]

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
        user = users_factories.UserFactory(email=self.identifier)

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

        assert push_testing.requests == [
            {
                "attribute_values": {
                    "date(u.date_created)": user.dateCreated.strftime("%Y-%m-%dT%H:%M:%S"),
                    "date(u.date_of_birth)": "2000-01-01T00:00:00",
                    "date(u.deposit_expiration_date)": user.deposit.expirationDate.strftime("%Y-%m-%dT%H:%M:%S"),
                    "u.credit": 50000,
                    "u.is_beneficiary": True,
                    "u.marketing_push_subscription": True,
                    "u.postal_code": None,
                },
                "user_id": user.id,
            }
        ]


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
        user = users_factories.UserFactory(dateOfBirth=datetime(2001, 1, 1))
        access_token = create_access_token(identity=user.email)

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {access_token}"}
        response = test_client.get("/native/v1/id_check_token")

        assert response.status_code == 200
        assert not response.json["token"]


class ShowEligibleCardTest:
    @pytest.mark.parametrize("age,expected", [(17, False), (18, True), (19, False)])
    def test_against_different_age(self, age, expected):
        date_of_birth = datetime.now() - relativedelta(years=age, days=5)
        date_of_creation = datetime.now() - relativedelta(years=4)
        user = users_factories.UserFactory.build(
            dateOfBirth=date_of_birth, dateCreated=date_of_creation, isBeneficiary=False, departementCode="93"
        )
        assert account_serializers.UserProfileResponse._show_eligible_card(user) == expected

    @pytest.mark.parametrize("beneficiary,expected", [(False, True), (True, False)])
    def test_against_beneficiary(self, beneficiary, expected):
        date_of_birth = datetime.now() - relativedelta(years=18, days=5)
        date_of_creation = datetime.now() - relativedelta(years=4)
        user = users_factories.UserFactory.build(
            dateOfBirth=date_of_birth, dateCreated=date_of_creation, isBeneficiary=beneficiary, departementCode="93"
        )
        assert account_serializers.UserProfileResponse._show_eligible_card(user) == expected

    @pytest.mark.parametrize("departement,expected", [("93", True), ("92", False)])
    def test_against_departement(self, departement, expected):
        date_of_birth = datetime.now() - relativedelta(years=18, days=5)
        date_of_creation = datetime.now() - relativedelta(years=4)
        user = users_factories.UserFactory.build(
            dateOfBirth=date_of_birth, dateCreated=date_of_creation, isBeneficiary=False, departementCode=departement
        )
        assert account_serializers.UserProfileResponse._show_eligible_card(user) == expected

    def test_user_eligible_but_created_after_18(self):
        date_of_birth = datetime.now() - relativedelta(years=18, days=5)
        date_of_creation = datetime.now()
        user = users_factories.UserFactory.build(
            dateOfBirth=date_of_birth, dateCreated=date_of_creation, isBeneficiary=False
        )
        assert account_serializers.UserProfileResponse._show_eligible_card(user) == False
