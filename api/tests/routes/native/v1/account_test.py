import dataclasses
import logging
from datetime import date
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from unittest import mock
from unittest.mock import patch

import fakeredis
import jwt
import pytest
import time_machine
from dateutil.relativedelta import relativedelta
from flask_jwt_extended.utils import create_access_token

import pcapi.core.finance.models as finance_models
import pcapi.core.mails.testing as mails_testing
import pcapi.core.subscription.api as subscription_api
import pcapi.core.subscription.factories as subscription_factories
import pcapi.core.subscription.models as subscription_models
import pcapi.core.subscription.schemas as subscription_schemas
import pcapi.core.users.constants as users_constants
from pcapi import settings
from pcapi.connectors.google_oauth import GoogleUser
from pcapi.core import token as token_utils
from pcapi.core.achievements import models as achievements_models
from pcapi.core.achievements.factories import AchievementFactory
from pcapi.core.bookings import factories as booking_factories
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.factories import CancelledBookingFactory
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.finance import deposit_api
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.subscription.bonus import constants as bonus_constants
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users import testing as users_testing
from pcapi.core.users import young_status
from pcapi.core.users.api import create_phone_validation_token
from pcapi.core.users.email.repository import get_email_update_latest_event
from pcapi.core.users.utils import ALGORITHM_HS_256
from pcapi.models import db
from pcapi.notifications.push import testing as push_testing
from pcapi.notifications.sms import testing as sms_testing
from pcapi.routes.native.v1.serialization import account as account_serializers
from pcapi.utils import date as date_utils
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.postal_code import INELIGIBLE_POSTAL_CODES


pytestmark = pytest.mark.usefixtures("db_session")


class AccountTest:
    identifier = "email@example.com"

    def test_get_user_profile_without_authentication(self, client, app):
        users_factories.UserFactory(email=self.identifier)

        with assert_num_queries(0):  # User is not fetched if no token is provided
            response = client.get("/native/v1/me")
            assert response.status_code == 401

    def test_get_user_profile_not_found(self, client, app):
        users_factories.UserFactory(email=self.identifier)

        token = create_access_token("other-email@example.com", additional_claims={"user_claims": {"user_id": 0}})
        client.auth_header = {
            "Authorization": f"Bearer {token}",
        }

        with assert_num_queries(1):  # user
            response = client.get("/native/v1/me")
            assert response.status_code == 403

        assert response.json["email"] == ["Utilisateur introuvable"]

    def test_get_user_profile_not_active(self, client, app):
        user = users_factories.UserFactory(email=self.identifier, isActive=False)

        client.with_token(user)
        with assert_num_queries(1):  # user
            response = client.get("/native/v1/me")
            assert response.status_code == 403

        assert response.json["email"] == ["Utilisateur introuvable"]

    @time_machine.travel("2018-06-01", tick=False)
    @pytest.mark.features(ENABLE_NATIVE_CULTURAL_SURVEY=True)
    def test_get_user_profile(self, client, app):
        USER_DATA = {
            "email": self.identifier,
            "firstName": "john",
            "lastName": "doe",
            "phoneNumber": "+33102030405",
            "address": "123 rue de la paix",
            "postalCode": "74000",
            "city": "Annecy",
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
            activity=users_models.ActivityEnum.STUDENT.value,
            **USER_DATA,
        )
        users_factories.DepositGrantFactory(
            user=user, type=finance_models.DepositType.GRANT_15_17, dateCreated=datetime(2015, 2, 3)
        )

        booking = BookingFactory(user=user, amount=Decimal("123.45"))
        CancelledBookingFactory(user=user, amount=Decimal("123.45"))

        expected_num_queries = 7  # user + deposit + booking(from _get_booked_offers) + booking (from get_domains_credit) + achievement + fraud check + action_history
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/me")
            assert response.status_code == 200, response.json

        EXPECTED_DATA = {
            "id": user.id,
            "email": self.identifier,
            "firstName": "john",
            "lastName": "doe",
            "phoneNumber": "+33102030405",
            "bookedOffers": {str(booking.stock.offer.id): booking.id},
            "domainsCredit": {
                "all": {"initial": 30000, "remaining": 17655},
                "digital": {"initial": 10000, "remaining": 10000},
                "physical": None,
            },
            "birthDate": "2000-01-11",
            "qfBonificationStatus": subscription_models.QFBonificationStatus.NOT_ELIGIBLE.value,
            "depositType": "GRANT_18",
            "depositActivationDate": "2018-06-01T00:00:00Z",
            "firstDepositActivationDate": "2015-02-03T00:00:00Z",
            "depositExpirationDate": "2040-01-01T00:00:00Z",
            "eligibility": "age-18",
            "eligibilityEndDatetime": "2019-01-10T23:00:00Z",
            "eligibilityStartDatetime": "2015-01-10T23:00:00Z",
            "hasPassword": True,
            "hasProfileExpired": False,
            "isBeneficiary": True,
            "isEligibleForBeneficiaryUpgrade": False,
            "needsToFillCulturalSurvey": True,
            "roles": ["BENEFICIARY"],
            "recreditAmountToShow": None,
            "recreditTypeToShow": None,
            "remainingBonusAttempts": 10,
            "requiresIdCheck": True,
            "showEligibleCard": False,
            "subscriptions": {"marketingPush": True, "marketingEmail": True, "subscribedThemes": []},
            "subscriptionMessage": None,
            "status": {
                "statusType": young_status.YoungStatusType.BENEFICIARY.value,
                "subscriptionStatus": None,
            },
            "activityId": users_models.ActivityEnum.STUDENT.name,
            "currency": "EUR",
            "achievements": [],
            "street": "123 rue de la paix",
            "postalCode": "74000",
            "city": "Annecy",
        }

        assert response.json == EXPECTED_DATA

    def test_status_contains_subscription_status_when_eligible(self, client):
        user = users_factories.UserFactory(dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18))

        expected_num_queries = (
            6  # user + beneficiary_fraud_review + beneficiary_fraud_check + deposit + booking + achievement
        )

        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/me")

        assert response.json["status"] == {
            "statusType": young_status.YoungStatusType.ELIGIBLE.value,
            "subscriptionStatus": young_status.SubscriptionStatus.HAS_TO_COMPLETE_SUBSCRIPTION.value,
        }

    def test_get_user_not_beneficiary(self, client, app):
        user = users_factories.UserFactory(email=self.identifier)

        expected_num_queries = 5  # user + achievement + booking + deposit + fraud check

        client.with_token(user)

        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/me")
            assert response.status_code == 200

        assert not response.json["domainsCredit"]

    def test_get_user_profile_empty_first_name(self, client, app):
        user = users_factories.UserFactory(email=self.identifier, firstName="")

        expected_num_queries = 5  # user + achievement + booking + deposit + fraud check

        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/me")
            assert response.status_code == 200

        assert response.json["email"] == self.identifier
        assert response.json["firstName"] is None
        assert not response.json["isBeneficiary"]
        assert response.json["roles"] == []

    def test_get_user_profile_legacy_activity(self, client):
        user = users_factories.UserFactory(email=self.identifier, activity="activity not in enum")

        expected_num_queries = 5  # user + achievement + booking + deposit + fraud check
        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/me")

        assert response.status_code == 200
        assert "activity" not in response.json

    def test_get_user_profile_recredit_amount_to_show(self, client):
        with time_machine.travel(datetime.today() - relativedelta(years=1)):
            user = users_factories.BeneficiaryFactory(email=self.identifier, age=16)

        deposit_api.recredit_users()

        expected_num_queries = 1  # user
        expected_num_queries += 1  # achievements
        expected_num_queries += 1  # bookings (from _get_booked_offers)
        expected_num_queries += 1  # bookings (from get_domains_credit)
        expected_num_queries += 1  # beneficiary fraud checks
        expected_num_queries += 1  # user_profile_refresh_campaign.
        expected_num_queries += 1  # recredit

        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            me_response = client.get("/native/v1/me")

        assert user.age == 17
        assert me_response.json["recreditAmountToShow"] == 5000
        assert me_response.json["recreditTypeToShow"] == "Recredit17"

    @pytest.mark.features(ENABLE_UBBLE=False)
    def test_maintenance_message(self, client):
        """
        Test that when a user has no subscription message and when the
        whole beneficiary signup process has been deactivated, the call
        to /me returns a generic maintenance message.
        """
        user = users_factories.UserFactory(
            activity=users_models.ActivityEnum.STUDENT.value,
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18, days=5),
            email=self.identifier,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)
        client.with_token(user)

        expected_num_queries = 7  # user + beneficiary_fraud_review + beneficiary_fraud_check + user_profile_refresh_campaign + deposit + booking + achievement
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/me")
        assert response.status_code == 200

        msg = response.json["subscriptionMessage"]
        assert (
            msg["userMessage"]
            == "La vérification d'identité est momentanément indisponible. L'équipe du pass Culture met tout en oeuvre pour la rétablir au plus vite."
        )
        assert msg["callToAction"] is None
        assert msg["popOverIcon"] == subscription_schemas.PopOverIcon.CLOCK.value

    def test_subscription_message_with_call_to_action(self, client):
        user = users_factories.UserFactory(
            activity=users_models.ActivityEnum.STUDENT.value,
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18, days=5),
            email=self.identifier,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[subscription_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED],
        )

        client.with_token(user)
        expected_num_queries = 7  # user + beneficiary_fraud_review + beneficiary_fraud_check + user_profile_refresh_campaign + deposit + booking + achievement
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/me")
            assert response.status_code == 200

        msg = response.json["subscriptionMessage"]
        assert (
            msg["userMessage"]
            == "Le document d'identité que tu as présenté n'est pas accepté. S’il s’agit d’une pièce d’identité étrangère ou d’un titre de séjour français, tu dois passer par le site demarche.numerique.gouv.fr. Si non, tu peux réessayer avec un passeport ou une carte d’identité française en cours de validité."
        )
        assert msg["callToAction"] == {
            "callToActionIcon": "RETRY",
            "callToActionLink": f"{settings.WEBAPP_V2_URL}/verification-identite",
            "callToActionTitle": "Réessayer la vérification de mon identité",
        }
        assert msg["popOverIcon"] is None

    @pytest.mark.parametrize(
        "enable_cultural_survey,enable_native_cultural_survey",
        [(True, False), (False, True)],
    )
    def test_user_should_need_to_fill_cultural_survey(
        self, features, client, enable_cultural_survey, enable_native_cultural_survey
    ):
        user = users_factories.UserFactory(age=18)

        expected_num_queries = 6  # user + booking + deposit + beneficiary_fraud_review * 2 + achievement

        client.with_token(user)
        features.ENABLE_CULTURAL_SURVEY = enable_cultural_survey
        features.ENABLE_NATIVE_CULTURAL_SURVEY = enable_native_cultural_survey
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/me")

        assert response.json["needsToFillCulturalSurvey"] == True

    @pytest.mark.features(ENABLE_CULTURAL_SURVEY=True, ENABLE_NATIVE_CULTURAL_SURVEY=True)
    def test_not_eligible_user_should_not_need_to_fill_cultural_survey(self, client):
        user = users_factories.UserFactory(age=4)

        expected_num_queries = 5  # user + achievement + booking + deposit + fraud check

        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/me")

        assert not response.json["needsToFillCulturalSurvey"]

    @pytest.mark.features(ENABLE_CULTURAL_SURVEY=False, ENABLE_NATIVE_CULTURAL_SURVEY=False)
    def test_cultural_survey_disabled(self, client):
        user = users_factories.UserFactory(age=18)

        expected_num_queries = 6  # user + booking + deposit + beneficiary_fraud_review * 2 + achievement

        client.with_token(user)
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/me")

        assert not response.json["needsToFillCulturalSurvey"]

    def test_num_queries_with_next_step(self, client):
        user = users_factories.UserFactory(
            activity=users_models.ActivityEnum.STUDENT.value,
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18, days=5),
            email=self.identifier,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[subscription_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED],
        )
        client.with_token(user)

        response = client.get("/native/v1/me")
        assert response.status_code == 200
        client.with_token(user)
        n_queries = 1  # get user
        n_queries += 1  # get bookings

        with assert_num_queries(n_queries):
            response = client.get("/native/v1/me")

    def test_num_queries_beneficiary(self, client):
        user = users_factories.BeneficiaryGrant18Factory()

        client.with_token(user)

        n_queries = 1  # user
        n_queries += 1  # user bookings
        n_queries += 1  # deposit
        n_queries += 1  # deposit bookings
        n_queries += 1  # achievement
        n_queries += 1  # fraud check
        n_queries += 1  # action history
        with assert_num_queries(n_queries):
            response = client.get("/native/v1/me")
            assert response.status_code == 200

    def should_display_cultural_survey_if_beneficiary(self, client):
        user = users_factories.BeneficiaryGrant18Factory()

        expected_num_queries = 7  # user + deposit + booking(from _get_booked_offers) + booking (from get_domains_credit) + achievement + fraud check + action history

        client.with_token(user)

        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/me")
            assert response.status_code == 200
        assert response.json["needsToFillCulturalSurvey"] is True

    def test_user_without_password(self, client):
        sso = users_factories.SingleSignOnFactory()
        user = sso.user
        user.password = None

        expected_num_queries = 5  # user + achievements + bookings + deposit + fraud check
        with assert_num_queries(expected_num_queries):
            response = client.with_token(user).get("/native/v1/me")
            assert response.status_code == 200, response.json

        assert response.json["hasPassword"] == False

    def test_currency_pacific_franc(self, client):
        user = users_factories.UserFactory(departementCode="988", postalCode="98818")

        expected_num_queries = 6  # user*2 + achievements + bookings + deposit + fraud check
        with assert_num_queries(expected_num_queries):
            response = client.with_token(user).get("/native/v1/me")

        assert response.status_code == 200, response.json
        assert response.json["currency"] == "XPF"

    def test_achievements(self, client):
        user = users_factories.UserFactory()
        now = date_utils.get_naive_utc_now()
        last_week = now - timedelta(days=7)
        achievement_1 = AchievementFactory(
            user=user,
            name=achievements_models.AchievementEnum.FIRST_MOVIE_BOOKING,
            unlockedDate=last_week,
            seenDate=last_week,
        )
        achievement_2 = AchievementFactory(
            user=user, name=achievements_models.AchievementEnum.FIRST_BOOK_BOOKING, unlockedDate=now
        )

        response = client.with_token(user).get("/native/v1/me")

        assert response.status_code == 200, response.json
        assert response.json["achievements"] == [
            {
                "id": achievement_1.id,
                "name": achievements_models.AchievementEnum.FIRST_MOVIE_BOOKING.name,
                "unlockedDate": format_into_utc_date(last_week),
                "seenDate": format_into_utc_date(last_week),
            },
            {
                "id": achievement_2.id,
                "name": achievements_models.AchievementEnum.FIRST_BOOK_BOOKING.name,
                "unlockedDate": format_into_utc_date(now),
                "seenDate": None,
            },
        ]

    def test_user_profile_has_expired(self, client):
        campaign_date = date_utils.get_naive_utc_now() + relativedelta(days=30)
        users_factories.UserProfileRefreshCampaignFactory(campaignDate=campaign_date)
        before_profile_expiry_date = campaign_date - relativedelta(days=1)
        user = users_factories.BeneficiaryFactory(beneficiaryFraudChecks__dateCreated=before_profile_expiry_date)

        response = client.with_token(user).get("/native/v1/me")

        assert response.status_code == 200
        assert response.json["hasProfileExpired"]

    def test_user_profile_is_up_to_date(self, client):
        campaign_date = date_utils.get_naive_utc_now() + relativedelta(days=30)
        before_profile_expiry_date = campaign_date - relativedelta(days=1)
        users_factories.UserProfileRefreshCampaignFactory(campaignDate=campaign_date)
        user = users_factories.PhoneValidatedUserFactory(dateCreated=before_profile_expiry_date)
        subscription_factories.ProfileCompletionFraudCheckFactory(
            user=user, dateCreated=campaign_date + relativedelta(days=1)
        )

        response = client.with_token(user).get("/native/v1/me")

        assert response.status_code == 200
        assert not response.json["hasProfileExpired"]

    def test_user_profile_has_expired_past_campaign(self, client):
        campaign_date = date_utils.get_naive_utc_now() - relativedelta(days=1)
        users_factories.UserProfileRefreshCampaignFactory(campaignDate=campaign_date, isActive=True)
        before_campaign_date = campaign_date - relativedelta(days=1)
        user = users_factories.BeneficiaryFactory(beneficiaryFraudChecks__dateCreated=before_campaign_date)

        response = client.with_token(user).get("/native/v1/me")

        assert response.status_code == 200
        assert response.json["hasProfileExpired"] is True

    def test_user_profile_is_up_to_date_through_action_history(self, client):
        campaign_date = date_utils.get_naive_utc_now() + relativedelta(days=30)
        users_factories.UserProfileRefreshCampaignFactory(campaignDate=campaign_date)
        before_profile_expiry_date = campaign_date - relativedelta(days=1)
        user = users_factories.PhoneValidatedUserFactory(dateCreated=before_profile_expiry_date)
        history_factories.ActionHistoryFactory(
            user=user,
            actionType=history_models.ActionType.INFO_MODIFIED,
            extraData={
                "modified_info": {
                    "city": {"new_info": "Paris", "old_info": None},
                    "address": {"new_info": "33 quai d'Orsay", "old_info": None},
                    "postalCode": {"new_info": "75007", "old_info": None},
                }
            },
            actionDate=campaign_date + relativedelta(days=1),
        )

        response = client.with_token(user).get("/native/v1/me")

        assert response.status_code == 200
        assert not response.json["hasProfileExpired"]

    def test_user_profile_has_not_expired_because_never_been_completed(self, client):
        campaign_date = date_utils.get_naive_utc_now() + relativedelta(days=30)
        users_factories.UserProfileRefreshCampaignFactory(campaignDate=campaign_date)
        user = users_factories.PhoneValidatedUserFactory()

        response = client.with_token(user).get("/native/v1/me")

        assert response.status_code == 200
        assert response.json["hasProfileExpired"] is False

    def test_free_beneficiary_profile_can_not_expire(self, client):
        campaign_date = date_utils.get_naive_utc_now() + relativedelta(days=30)
        users_factories.UserProfileRefreshCampaignFactory(campaignDate=campaign_date)
        before_campaign_date = campaign_date - relativedelta(days=1)
        user = users_factories.FreeBeneficiaryFactory(beneficiaryFraudChecks__dateCreated=before_campaign_date)

        response = client.with_token(user).get("/native/v1/me")

        assert response.status_code == 200
        assert response.json["hasProfileExpired"] is False

    def test_get_user_profile_bonification_status_is_eligible(self, client):
        user = users_factories.BeneficiaryFactory(age=18)
        response = client.with_token(user).get("/native/v1/me")
        assert response.status_code == 200
        assert response.json["qfBonificationStatus"] == "eligible"

    @pytest.mark.parametrize(
        "fraud_check_status",
        [
            subscription_models.FraudCheckStatus.CANCELED,
            subscription_models.FraudCheckStatus.ERROR,
        ],
    )
    def test_get_user_profile_bonification_status_is_eligible_after_error(self, client, fraud_check_status):
        user = users_factories.BeneficiaryFactory(age=18)
        subscription_factories.BonusFraudCheckFactory(status=fraud_check_status, user=user)
        response = client.with_token(user).get("/native/v1/me")
        assert response.status_code == 200
        assert response.json["qfBonificationStatus"] == "eligible"

    @pytest.mark.parametrize(
        "reason_code,expected_qf_bonification_status",
        [
            (
                subscription_models.FraudReasonCode.NOT_IN_TAX_HOUSEHOLD,
                subscription_models.QFBonificationStatus.NOT_IN_TAX_HOUSEHOLD,
            ),
            (
                subscription_models.FraudReasonCode.QUOTIENT_FAMILIAL_TOO_HIGH,
                subscription_models.QFBonificationStatus.QUOTIENT_FAMILIAL_TOO_HIGH,
            ),
            (
                subscription_models.FraudReasonCode.CUSTODIAN_NOT_FOUND,
                subscription_models.QFBonificationStatus.CUSTODIAN_NOT_FOUND,
            ),
        ],
    )
    def test_get_user_profile_bonification_status_ko(self, client, reason_code, expected_qf_bonification_status):
        user = users_factories.BeneficiaryFactory(age=18)
        subscription_factories.BonusFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.KO,
            reasonCodes=[reason_code],
            user=user,
        )
        response = client.with_token(user).get("/native/v1/me")
        assert response.status_code == 200
        assert response.json["qfBonificationStatus"] == expected_qf_bonification_status.value

    def test_get_user_profile_bonification_status_granted(self, client):
        user = users_factories.BeneficiaryFactory(age=18)
        subscription_factories.BonusFraudCheckFactory(user=user, status=subscription_models.FraudCheckStatus.OK)
        response = client.with_token(user).get("/native/v1/me")
        assert response.status_code == 200
        assert response.json["qfBonificationStatus"] == subscription_models.QFBonificationStatus.GRANTED.value

    def test_get_user_profile_bonification_status_too_many_retries(self, client):
        user = users_factories.BeneficiaryFactory(age=18)
        subscription_factories.BonusFraudCheckFactory.create_batch(
            size=users_constants.MAX_QF_BONUS_RETRIES,
            user=user,
            status=subscription_models.FraudCheckStatus.KO,
            reasonCodes=[subscription_models.FraudReasonCode.NOT_IN_TAX_HOUSEHOLD],
        )
        response = client.with_token(user).get("/native/v1/me")
        assert response.status_code == 200
        assert response.json["qfBonificationStatus"] == subscription_models.QFBonificationStatus.TOO_MANY_RETRIES.value

    def test_get_user_profile_bonification_status_is_not_eligible_for_under_17(self, client):
        user = users_factories.BeneficiaryFactory(age=17)
        response = client.with_token(user).get("/native/v1/me")
        assert response.status_code == 200
        assert response.json["qfBonificationStatus"] == subscription_models.QFBonificationStatus.NOT_ELIGIBLE.value

    def test_get_user_profile_bonification_status_is_not_eligible_for_non_beneficiary(self, client):
        user = users_factories.HonorStatementValidatedUserFactory(age=18)
        response = client.with_token(user).get("/native/v1/me")
        assert response.status_code == 200
        assert response.json["qfBonificationStatus"] == subscription_models.QFBonificationStatus.NOT_ELIGIBLE.value

    def test_get_user_profile_bonification_status_unknown_ko(self, client):
        user = users_factories.BeneficiaryFactory(age=18)
        subscription_factories.BonusFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.KO,
            reasonCodes=None,
            user=user,
        )
        response = client.with_token(user).get("/native/v1/me")
        assert response.status_code == 200
        assert response.json["qfBonificationStatus"] == subscription_models.QFBonificationStatus.UNKNOWN_KO.value

    def test_get_user_profile_bonification_status_takes_latest_fraud_check(self, client):
        user = users_factories.BeneficiaryFactory(age=18)
        subscription_factories.BonusFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.KO,
            reasonCodes=None,
            dateCreated=date_utils.get_naive_utc_now() - timedelta(days=7),
            user=user,
        )
        subscription_factories.BonusFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.OK,
            reasonCodes=None,
            user=user,
        )
        response = client.with_token(user).get("/native/v1/me")
        assert response.status_code == 200
        assert response.json["qfBonificationStatus"] == subscription_models.QFBonificationStatus.GRANTED.value

    def test_get_user_profile_recredit_type(self, client):
        user = users_factories.BeneficiaryFactory(age=18)
        deposit_api.recredit_bonus_credit(user)
        response = client.with_token(user).get("/native/v1/me")
        assert response.status_code == 200
        assert response.json["recreditAmountToShow"] == 50_00
        assert response.json["recreditTypeToShow"] == "BonusCredit"

    def test_get_user_profile_remaining_bonus_attempts_after_success(self, client):
        user = users_factories.BeneficiaryFactory(age=18)
        subscription_factories.BonusFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.KO,
            reasonCodes=None,
            dateCreated=date_utils.get_naive_utc_now() - timedelta(days=7),
            user=user,
        )
        subscription_factories.BonusFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.OK,
            reasonCodes=None,
            user=user,
        )
        response = client.with_token(user).get("/native/v1/me")
        assert response.status_code == 200
        assert response.json["remainingBonusAttempts"] == 0

    def test_get_user_profile_remaining_bonus_attempts(self, client):
        user = users_factories.BeneficiaryFactory(age=18)
        subscription_factories.BonusFraudCheckFactory.create_batch(
            size=5,
            status=subscription_models.FraudCheckStatus.KO,
            reasonCodes=None,
            dateCreated=date_utils.get_naive_utc_now() - timedelta(days=7),
            user=user,
        )
        subscription_factories.BonusFraudCheckFactory(
            # This one should not be taken into account in remaining attempts
            status=subscription_models.FraudCheckStatus.KO,
            user=user,
            reason=f"{bonus_constants.BACKOFFICE_ORIGIN_START}, User 123",
        )
        response = client.with_token(user).get("/native/v1/me")
        assert response.status_code == 200
        assert response.json["remainingBonusAttempts"] == 5


class AccountCreationTest:
    identifier = "email@example.com"

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_account_creation(self, mocked_check_recaptcha_token_is_valid, client, app):
        assert db.session.query(users_models.User).first() is None
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

        expected_num_queries = 1  # user
        expected_num_queries += 1  # user (insert)
        expected_num_queries += 1  # bookings
        expected_num_queries += 1  # favorites
        expected_num_queries += 1  # deposit
        expected_num_queries += 1  # action history
        expected_num_queries += 1  # achievements
        with assert_num_queries(expected_num_queries):
            response = client.post("/native/v1/account", json=data)
            assert response.status_code == 204, response.json

        user = db.session.query(users_models.User).first()
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

        email_validation_token_exists = token_utils.Token.token_exists(
            token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION, user.id
        )

        assert email_validation_token_exists

    @patch("pcapi.connectors.api_recaptcha.check_recaptcha_token_is_valid")
    def test_too_young_account_creation(self, mocked_check_recaptcha_token_is_valid, client):
        assert db.session.query(users_models.User).first() is None
        data = {
            "email": "John.doe@example.com",
            "password": "Aazflrifaoi6@",
            "birthdate": (date_utils.get_naive_utc_now() - relativedelta(years=15, days=-1)).date().isoformat(),
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

        trusted_device = db.session.query(users_models.TrustedDevice).one()

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

        assert db.session.query(users_models.TrustedDevice).count() == 0

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

    @pytest.mark.parametrize(
        "invalid_email",
        [
            "[hello]@example.com",
            "hello@world@example.com",
            "hello$@example.com",
            "hello|world@example.com",
            "hello·world@example.com",
        ],
    )
    def test_account_creation_with_invalid_email(self, client, invalid_email):
        data = {
            "email": invalid_email,
            "password": "user@AZERTY1234",
            "birthdate": "1960-12-31",
            "notifications": False,
            "token": "dummy token",
            "marketingEmailSubscription": False,
        }
        response = client.post("/native/v1/account", json=data)

        assert response.status_code == 400, response.json
        assert "email" in response.json


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
            type_=token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION,
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

        user = db.session.query(users_models.User).one()
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
                "birthdate": (date_utils.get_naive_utc_now() - relativedelta(years=15, days=-1)).date().isoformat(),
                "notifications": True,
                "token": "gnagna",
                "marketingEmailSubscription": True,
            },
        )

        assert response.status_code == 400
        assert "email" in response.json
        assert (
            db.session.query(users_models.User)
            .filter(users_models.User.email == "docteur.cuesta@passculture.app")
            .count()
            == 1
        )

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
                "birthdate": (date_utils.get_naive_utc_now() - relativedelta(years=15, days=-1)).date().isoformat(),
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

        trusted_device = db.session.query(users_models.TrustedDevice).one()
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
        assert db.session.query(users_models.TrustedDevice).count() == 0

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

        user = db.session.query(users_models.User).one()

        assert response.status_code == 200, response.json
        try_dms_orphan_adoption_mock.assert_called_once_with(user)


class UserProfileUpdateTest:
    identifier = "email@example.com"

    def test_update_user_push_notifications_subscription(self, client):
        password = "some_random_string"
        user = users_factories.UserFactory(email=self.identifier, password=password)

        client.with_token(user)
        response = client.patch(
            "/native/v1/profile",
            json={
                "subscriptions": {"marketingPush": True, "marketingEmail": False, "subscribedThemes": ["cinema"]},
            },
        )

        assert response.status_code == 200

        user = db.session.query(users_models.User).filter_by(email=self.identifier).first()

        assert user.get_notification_subscriptions().marketing_push
        assert not user.get_notification_subscriptions().marketing_email
        assert user.get_notification_subscriptions().subscribed_themes == ["cinema"]
        assert len(push_testing.requests) == 2

    def test_unsubscribe_push_notifications(self, client):
        user = users_factories.UserFactory(email=self.identifier)

        client.with_token(user)
        response = client.patch(
            "/native/v1/profile",
            json={"subscriptions": {"marketingPush": False, "marketingEmail": False, "subscribedThemes": []}},
        )

        assert response.status_code == 200

        user = db.session.query(users_models.User).filter_by(email=self.identifier).first()
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

        action = db.session.query(history_models.ActionHistory).one()
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
        user = users_factories.UserFactory(
            email=self.identifier,
            notificationSubscriptions={
                "marketing_push": True,
                "marketing_email": True,
                "subscribed_themes": ["musique", "visites"],
            },
        )

        client.with_token(user)
        with caplog.at_level(logging.INFO):
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

    def test_address_update(self, client):
        user = users_factories.UserFactory(email=self.identifier)

        client.with_token(user)
        response = client.patch("/native/v1/profile", json={"address": "new address"})

        assert response.status_code == 200
        assert user.address == "new address"

    def test_postal_code_update(self, client):
        user = users_factories.UserFactory(email=self.identifier)

        client.with_token(user)
        response = client.patch("/native/v1/profile", json={"postalCode": "38000", "city": "Grenoble"})

        assert response.status_code == 200
        assert user.postalCode == "38000"
        assert user.city == "Grenoble"

    @pytest.mark.parametrize("postal_code", INELIGIBLE_POSTAL_CODES)
    def test_ineligible_postal_code_update(self, client, postal_code):
        user = users_factories.UserFactory(email=self.identifier)

        response = client.with_token(user).patch(
            "/native/v1/profile", json={"postalCode": postal_code, "city": "Grenoble"}
        )

        assert response.status_code == 400
        assert response.json["code"] == "INELIGIBLE_POSTAL_CODE"
        assert user.postalCode != postal_code

    @time_machine.travel("2022-03-17 09:00:00")
    def test_activity_update(self, client):
        user = users_factories.UserFactory(email=self.identifier)

        client.with_token(user)
        response = client.patch("/native/v1/profile", json={"activity_id": users_models.ActivityEnum.UNEMPLOYED.name})

        assert response.status_code == 200
        assert user.activity == users_models.ActivityEnum.UNEMPLOYED.value

        android_batch_request = push_testing.requests[0]
        ios_batch_request = push_testing.requests[1]
        android_batch_attributes = android_batch_request.get("attribute_values", {})
        ios_batch_attributes = ios_batch_request.get("attribute_values", {})

        assert android_batch_attributes.get("date(u.last_status_update_date)") == "2022-03-17T09:00:00"
        assert ios_batch_attributes.get("date(u.last_status_update_date)") == "2022-03-17T09:00:00"

    @pytest.mark.parametrize("requested_phone_number", ["0601020304", "+33601020304"])
    def test_phone_number_unchanged(self, client, requested_phone_number):
        user = users_factories.UserFactory(
            email=self.identifier,
            phoneNumber="+33601020304",
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )

        response = client.with_token(user).patch("/native/v1/profile", json={"phoneNumber": requested_phone_number})

        assert response.status_code == 200
        assert user.phoneNumber == "+33601020304"
        assert user.phoneValidationStatus == users_models.PhoneValidationStatusType.VALIDATED

    def test_phone_number_update(self, client):
        user = users_factories.UserFactory(
            email=self.identifier, phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )

        response = client.with_token(user).patch("/native/v1/profile", json={"phoneNumber": "0601020304"})

        assert response.status_code == 200
        assert user.phoneNumber == "+33601020304"
        assert user.phoneValidationStatus is None

    def test_invalid_phone_number_update(self, client):
        user = users_factories.UserFactory(email=self.identifier)

        response = client.with_token(user).patch("/native/v1/profile", json={"phoneNumber": "060102030405"})

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_PHONE_NUMBER"

    def test_invalid_phone_number_country_code_update(self, client):
        user = users_factories.UserFactory(email=self.identifier)

        response = client.with_token(user).patch("/native/v1/profile", json={"phoneNumber": "+46766123456"})

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_COUNTRY_CODE"

    def test_empty_patch(self, client):
        user = users_factories.UserFactory(
            email=self.identifier,
            activity=users_models.ActivityEnum.UNEMPLOYED.value,
            address="1 boulevard de la Libération",
            city="Grenoble",
            postalCode="38000",
            notificationSubscriptions={
                "marketing_push": True,
                "marketing_email": True,
                "subscribed_themes": ["musique", "visites"],
            },
            _phoneNumber="+33601020304",
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )

        client.with_token(user)
        response = client.patch("/native/v1/profile", json={})

        assert response.status_code == 200
        assert user.activity == users_models.ActivityEnum.UNEMPLOYED.value
        assert user.address == "1 boulevard de la Libération"
        assert user.city == "Grenoble"
        assert user.postalCode == "38000"
        assert user.notificationSubscriptions == {
            "marketing_push": True,
            "marketing_email": True,
            "subscribed_themes": ["musique", "visites"],
        }
        assert user.phoneNumber == "+33601020304"
        assert user.phoneValidationStatus == users_models.PhoneValidationStatusType.VALIDATED

        android_batch_request = push_testing.requests[0]
        ios_batch_request = push_testing.requests[1]
        android_batch_attributes = android_batch_request.get("attribute_values", {})
        ios_batch_attributes = ios_batch_request.get("attribute_values", {})

        assert "date(u.last_status_update_date)" not in android_batch_attributes
        assert "date(u.last_status_update_date)" not in ios_batch_attributes


class ResetRecreditAmountToShowTest:
    def test_update_user_profile_reset_recredit_amount_to_show(self, client, app):
        user = users_factories.UnderageBeneficiaryFactory(email="email@example.com", recreditAmountToShow=30)

        response = client.with_token(user).post("/native/v1/reset_recredit_amount_to_show")

        assert response.status_code == 200
        assert user.recreditAmountToShow is None


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

        user = db.session.get(users_models.User, user.id)
        assert user.email == self.new_email

    @patch("pcapi.core.subscription.dms.api.try_dms_orphan_adoption")
    def test_dms_adoption_on_email_validation_for_eligible_user(self, try_dms_orphan_adoption_mock, app, client):
        user = users_factories.UserFactory(
            email=self.old_email, dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18)
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

        user = db.session.get(users_models.User, user.id)
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

                user = db.session.get(users_models.User, user.id)
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
        token = token_utils.Token.create(
            type_=token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION,
            ttl=users_constants.EMAIL_CHANGE_TOKEN_LIFE_TIME,
            user_id=user.id,
            data={"new_email": "newemail@email.com"},
        )
        expiration_date = token.get_expiration_date_from_token()

        client = client.with_token(user)
        expected_num_queries = 1  # user_email
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/profile/token_expiration")
            assert response.status_code == 200

        expiration = datetime.fromisoformat(response.json["expiration"]).replace(tzinfo=None)
        delta = abs(expiration - expiration_date)
        assert delta == timedelta(seconds=0)

    def test_no_token(self, app, client):
        user = users_factories.UserFactory(email=self.email)

        client = client.with_token(user)
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
        email = "hello@example.com"
        for _i in range(3):
            response = client.post("/native/v1/resend_email_validation", json={"email": email})
            assert response.status_code == 204

        response = client.post("/native/v1/resend_email_validation", json={"email": email})

        assert response.status_code == 429
        assert response.json["code"] == "TOO_MANY_EMAIL_VALIDATION_RESENDS"
        assert response.json["message"] == "Le nombre de tentatives maximal est dépassé."


class EmailValidationRemainingResendsTest:
    def test_email_validation_remaining_resends(
        self,
        client,
    ):
        email = "hello@example.com"

        response = client.get(f"/native/v1/email_validation_remaining_resends/{email}")
        assert response.status_code == 200
        assert response.json["remainingResends"] == 3

        client.post("/native/v1/resend_email_validation", json={"email": email})
        response = client.get(f"/native/v1/email_validation_remaining_resends/{email}")

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
        with assert_num_queries(0):
            response = client.get("/native/v1/email_validation_remaining_resends/test@example.com")

        assert response.json["remainingResends"] == settings.MAX_EMAIL_RESENDS
        assert response.json["counterResetDatetime"] is None


class ShowEligibleCardTest:
    @pytest.mark.parametrize("age,expected", [(17, False), (18, True), (19, False)])
    def test_against_different_age(self, age, expected):
        date_of_birth = date_utils.get_naive_utc_now() - relativedelta(years=age, days=5)
        date_of_creation = date_utils.get_naive_utc_now() - relativedelta(years=4)
        user = users_factories.UserFactory(dateOfBirth=date_of_birth, dateCreated=date_of_creation)
        assert account_serializers.UserProfileResponse.from_orm(user).show_eligible_card == expected

    @pytest.mark.parametrize("beneficiary,expected", [(False, True), (True, False)])
    def test_against_beneficiary(self, beneficiary, expected):
        date_of_birth = date_utils.get_naive_utc_now() - relativedelta(years=18, days=5)
        date_of_creation = date_utils.get_naive_utc_now() - relativedelta(years=4)
        roles = [users_models.UserRole.BENEFICIARY] if beneficiary else []
        user = users_factories.UserFactory(
            dateOfBirth=date_of_birth,
            dateCreated=date_of_creation,
            roles=roles,
        )
        assert account_serializers.UserProfileResponse.from_orm(user).show_eligible_card == expected

    def test_user_eligible_but_created_after_18(self):
        date_of_birth = date_utils.get_naive_utc_now() - relativedelta(years=19, days=5)
        date_of_creation = date_utils.get_naive_utc_now()
        user = users_factories.UserFactory(dateOfBirth=date_of_birth, dateCreated=date_of_creation)
        assert account_serializers.UserProfileResponse.from_orm(user).show_eligible_card is False


class SendPhoneValidationCodeTest:
    def test_send_phone_validation_code(self, client, app):
        user = users_factories.UserFactory()
        client.with_token(user)

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
        assert token.get_expiration_date_from_token() >= date_utils.get_naive_utc_now() + timedelta(hours=10)
        assert token.get_expiration_date_from_token() < date_utils.get_naive_utc_now() + timedelta(hours=13)

        assert sms_testing.requests == [
            {"recipient": "+33601020304", "content": f"{token.encoded_token} est ton code de confirmation pass Culture"}
        ]
        assert len(token.encoded_token) == 6
        assert 0 <= int(token.encoded_token) < 1000000
        assert token.data["phone_number"] == "+33601020304"

        # validate phone number with generated code
        response = client.post("/native/v1/validate_phone_number", json={"code": token.encoded_token})

        assert response.status_code == 204
        user = db.session.get(users_models.User, user.id)
        assert user.is_phone_validated

    @pytest.mark.settings(MAX_SMS_SENT_FOR_PHONE_VALIDATION=1)
    def test_send_phone_validation_code_too_many_attempts(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18, days=5),
        )
        client.with_token(user)

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33601020304"})
        assert response.status_code == 204

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33601020304"})
        assert response.status_code == 400
        assert response.json["code"] == "TOO_MANY_SMS_SENT"

        # check that a fraud check has been created
        fraud_check = (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter_by(
                userId=user.id,
                type=subscription_models.FraudCheckType.PHONE_VALIDATION,
                thirdPartyId=f"PC-{user.id}",
                status=subscription_models.FraudCheckStatus.KO,
            )
            .one_or_none()
        )

        assert fraud_check is not None
        assert fraud_check.eligibilityType == users_models.EligibilityType.AGE17_18

        content = fraud_check.resultContent
        expected_reason = "Le nombre maximum de sms envoyés est atteint"
        assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.SMS_SENDING_LIMIT_REACHED]
        assert fraud_check.reason == expected_reason
        assert content["phone_number"] == "+33601020304"

    def test_send_phone_validation_code_already_beneficiary(self, client):
        user = users_factories.BeneficiaryGrant18Factory()
        client.with_token(user)

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33601020304"})

        assert response.status_code == 400

        assert not token_utils.SixDigitsToken.token_exists(token_utils.TokenType.PHONE_VALIDATION, user.id)

    def test_send_phone_validation_code_for_new_phone_with_already_beneficiary(self, client, app):
        user = users_factories.BeneficiaryGrant18Factory(
            isEmailValidated=True, phoneNumber="+33601020304", roles=[users_models.UserRole.BENEFICIARY]
        )
        client.with_token(user)

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33102030405"})

        assert response.status_code == 400

        assert not token_utils.SixDigitsToken.token_exists(token_utils.TokenType.PHONE_VALIDATION, user.id)
        db.session.refresh(user)
        assert user.phoneNumber == "+33601020304"

    def test_send_phone_validation_code_for_new_phone_updates_phone(self, client):
        user = users_factories.UserFactory(isEmailValidated=True, phoneNumber="+33601020304")
        client.with_token(user)

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33102030405"})

        assert response.status_code == 204

        db.session.refresh(user)
        assert user.phoneNumber == "+33102030405"

    def test_send_phone_validation_code_for_new_unvalidated_duplicated_phone_number(self, client, app):
        users_factories.UserFactory(isEmailValidated=True, phoneNumber="+33102030405")
        user = users_factories.UserFactory(isEmailValidated=True, phoneNumber="+33601020304")
        client.with_token(user)

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
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18, days=5),
        )
        client.with_token(user)

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
        fraud_check = (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter_by(
                userId=user.id,
                type=subscription_models.FraudCheckType.PHONE_VALIDATION,
                thirdPartyId=f"PC-{user.id}",
                status=subscription_models.FraudCheckStatus.KO,
            )
            .one_or_none()
        )

        assert fraud_check is not None
        assert fraud_check.eligibilityType == users_models.EligibilityType.AGE17_18

        content = fraud_check.resultContent
        assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.PHONE_ALREADY_EXISTS]
        assert fraud_check.reason == f"Le numéro est déjà utilisé par l'utilisateur {orig_user.id}"
        assert content["phone_number"] == "+33102030405"

        assert (
            subscription_api.get_phone_validation_subscription_item(user, users_models.EligibilityType.AGE18).status
            == subscription_schemas.SubscriptionItemStatus.KO
        )

    def test_send_phone_validation_code_with_invalid_number(self, client):
        # user's phone number should be in international format (E.164): +33601020304
        user = users_factories.UserFactory(isEmailValidated=True)
        client.with_token(user)

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "060102030405"})

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_PHONE_NUMBER"
        assert not token_utils.SixDigitsToken.token_exists(token_utils.TokenType.PHONE_VALIDATION, user.id)

    def test_send_phone_validation_code_with_non_french_number(self, client):
        user = users_factories.UserFactory(isEmailValidated=True)
        client.with_token(user)

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+46766123456"})

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_COUNTRY_CODE"
        assert response.json["message"] == "L'indicatif téléphonique n'est pas accepté"
        assert not token_utils.SixDigitsToken.token_exists(token_utils.TokenType.PHONE_VALIDATION, user.id)

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(userId=user.id).one()
        assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.INVALID_PHONE_COUNTRY_CODE]
        assert fraud_check.type == subscription_models.FraudCheckType.PHONE_VALIDATION

    @pytest.mark.settings(BLACKLISTED_SMS_RECIPIENTS={"+33601020304"})
    def test_blocked_phone_number(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18, days=5),
        )
        client.with_token(user)

        response = client.post("/native/v1/send_phone_validation_code", json={"phoneNumber": "+33601020304"})

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_PHONE_NUMBER"

        assert not token_utils.SixDigitsToken.token_exists(token_utils.TokenType.PHONE_VALIDATION, user.id)
        db.session.refresh(user)
        assert user.phoneNumber is None

        # check that a fraud check has been created
        fraud_check = (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter_by(
                userId=user.id,
                type=subscription_models.FraudCheckType.PHONE_VALIDATION,
                thirdPartyId=f"PC-{user.id}",
                status=subscription_models.FraudCheckStatus.KO,
            )
            .one_or_none()
        )

        assert fraud_check.eligibilityType == users_models.EligibilityType.AGE17_18

        content = fraud_check.resultContent
        assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.BLACKLISTED_PHONE_NUMBER]
        assert fraud_check.reason == "Le numéro saisi est interdit"
        assert content["phone_number"] == "+33601020304"


class ValidatePhoneNumberTest:
    mock_redis_client = fakeredis.FakeStrictRedis()

    def test_validate_phone_number(self, client, app):
        user = users_factories.UserFactory(
            phoneNumber="+33607080900", dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18)
        )
        client.with_token(user)
        token = create_phone_validation_token(user, "+33607080900")

        # try one attempt with wrong code
        client.post("/native/v1/validate_phone_number", {"code": "wrong code"})
        response = client.post("/native/v1/validate_phone_number", {"code": token.encoded_token})

        assert response.status_code == 204
        user = db.session.get(users_models.User, user.id)
        assert user.is_phone_validated
        assert not user.has_beneficiary_role

        fraud_check = (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter_by(user=user, type=subscription_models.FraudCheckType.PHONE_VALIDATION)
            .one()
        )
        assert fraud_check.status == subscription_models.FraudCheckStatus.OK
        assert fraud_check.eligibilityType == users_models.EligibilityType.AGE17_18

        assert not token_utils.SixDigitsToken.token_exists(token_utils.TokenType.PHONE_VALIDATION, user.id)

        assert int(app.redis_client.get(f"phone_validation_attempts_user_{user.id}")) == 2

    def test_can_not_validate_phone_number_with_first_sent_code(self, client, app):
        first_number = "+33611111111"
        second_number = "+33622222222"
        user = users_factories.UserFactory(phoneNumber=second_number)
        client.with_token(user)
        first_token = create_phone_validation_token(user, first_number)
        create_phone_validation_token(user, second_number)

        response = client.post("/native/v1/validate_phone_number", {"code": first_token.encoded_token})

        assert response.status_code == 400
        user = db.session.get(users_models.User, user.id)
        assert not user.is_phone_validated

        assert int(app.redis_client.get(f"phone_validation_attempts_user_{user.id}")) == 1

    def test_validate_phone_number_and_become_beneficiary(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18, days=5),
            phoneNumber="+33607080900",
            activity="Lycéen",
        )

        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user, type=subscription_models.FraudCheckType.UBBLE, status=subscription_models.FraudCheckStatus.OK
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
        )
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)

        client.with_token(user)
        token = create_phone_validation_token(user, "+33607080900")

        response = client.post("/native/v1/validate_phone_number", {"code": token.encoded_token})

        assert response.status_code == 204
        user = db.session.get(users_models.User, user.id)
        assert user.is_phone_validated
        assert user.has_beneficiary_role

    @pytest.mark.settings(MAX_PHONE_VALIDATION_ATTEMPTS=1)
    def test_validate_phone_number_too_many_attempts(self, client, app):
        user = users_factories.UserFactory(
            phoneNumber="+33607080900",
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18, days=5),
        )
        client.with_token(user)
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

        fraud_checks = (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter_by(
                userId=user.id,
                type=subscription_models.FraudCheckType.PHONE_VALIDATION,
                thirdPartyId=f"PC-{user.id}",
            )
            .all()
        )
        for fraud_check in fraud_checks:
            assert fraud_check.eligibilityType == users_models.EligibilityType.AGE17_18

            expected_reason = f"Le nombre maximum de tentatives de validation est atteint: {attempts_count}"
            content = fraud_check.resultContent
            assert fraud_check.reasonCodes == [
                subscription_models.FraudReasonCode.PHONE_VALIDATION_ATTEMPTS_LIMIT_REACHED
            ]

            assert fraud_check.reason == expected_reason
            assert content["phone_number"] == "+33607080900"

    @pytest.mark.settings(MAX_SMS_SENT_FOR_PHONE_VALIDATION=1)
    @time_machine.travel("2022-05-17 15:00")
    def test_phone_validation_remaining_attempts(self, client):
        user = users_factories.UserFactory(dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18, days=5))
        client.with_token(user)
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
        client.with_token(user)
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
        assert db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(userId=user.id).first() is None

        response = client.post("/native/v1/validate_phone_number", {"code": "mauvais-code"})
        assert response.status_code == 400
        assert response.json["code"] == "TOO_MANY_VALIDATION_ATTEMPTS"
        assert response.json["message"] == "Le nombre de tentatives maximal est dépassé"

        fraud_check = db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(userId=user.id).one()
        assert fraud_check.type == subscription_models.FraudCheckType.PHONE_VALIDATION
        assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.PHONE_VALIDATION_ATTEMPTS_LIMIT_REACHED]

        assert not db.session.get(users_models.User, user.id).is_phone_validated
        assert token_utils.SixDigitsToken.token_exists(token_utils.TokenType.PHONE_VALIDATION, user.id)

    def test_expired_code(self, client):
        with mock.patch("flask.current_app.redis_client", self.mock_redis_client):
            user = users_factories.UserFactory(phoneNumber="+33607080900")
            token = create_phone_validation_token(user, "+33607080900")

            with time_machine.travel(date_utils.get_naive_utc_now() + timedelta(hours=15)):
                client.with_token(user)
                response = client.post("/native/v1/validate_phone_number", {"code": token.encoded_token})

            assert response.status_code == 400
            assert response.json["code"] == "INVALID_VALIDATION_CODE"

            assert not db.session.get(users_models.User, user.id).is_phone_validated
            assert token_utils.SixDigitsToken.token_exists(token_utils.TokenType.PHONE_VALIDATION, user.id)

    def test_validate_phone_number_with_already_validated_phone(self, client):
        users_factories.UserFactory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            phoneNumber="+33607080900",
            roles=[users_models.UserRole.BENEFICIARY],
        )
        user = users_factories.UserFactory(phoneNumber="+33607080900")
        client.with_token(user)
        token = create_phone_validation_token(user, "+33607080900")

        # try one attempt with wrong code
        response = client.post("/native/v1/validate_phone_number", {"code": token.encoded_token})

        assert response.status_code == 400
        user = db.session.get(users_models.User, user.id)
        assert not user.is_phone_validated


class SuspendAccountTest:
    def test_suspend_account(self, client, app):
        booking = booking_factories.BookingFactory()
        user = booking.user

        client.with_token(user)
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

        client.with_token(user)
        response = client.post("/native/v1/account/suspend")

        # Any API call is forbidden for suspended user
        assert response.status_code == 403
        db.session.refresh(user)
        assert not user.isActive
        assert user.suspension_reason == reason
        assert len(user.suspension_action_history) == 1


def build_user_at_id_check(age):
    user = users_factories.UserFactory(
        dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=age, days=5),
        phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
    )
    subscription_factories.ProfileCompletionFraudCheckFactory(
        user=user,
        eligibilityType=users_models.EligibilityType.AGE18,
        resultContent=subscription_factories.ProfileCompletionContentFactory(first_name="Sally", last_name="Mara"),
    )
    return user


class AccountSecurityTest:
    def test_account_hacker_changes_password(self, client, app):
        """
        This scenario has been suggested by a security bug hunter: it is possible for a hacker to register with the
        email someone else registered earlier, before the hacked user clicks on email confirmation link. The hacker can
        change user's password this way.
        """
        assert db.session.query(users_models.User).first() is None
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

        user = db.session.query(users_models.User).first()
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

        assert db.session.query(users_models.User).count() == 1
        user = db.session.query(users_models.User).first()
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

        client.with_token(user)
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
            client.with_token(user)

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
        client.with_token(user)
        response = client.get("/native/v1/account/suspension_status")

        assert response.status_code == 200
        assert response.json["status"] == status


class UnsuspendAccountTest:
    def test_suspended_upon_user_request(self, client):
        user = users_factories.BeneficiaryGrant18Factory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )

        client.with_token(user)
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

        response = client.with_token(user).post("/native/v1/account/unsuspend")
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

        response = client.with_token(user).post("/native/v1/account/unsuspend")
        self.assert_code_and_not_active(response, user, "UNSUSPENSION_NOT_ALLOWED")

    def test_error_when_suspension_time_limit_reached(self, client):
        user = users_factories.BeneficiaryGrant18Factory(isActive=False)

        suspension_date = date.today() - timedelta(days=users_constants.ACCOUNT_UNSUSPENSION_DELAY + 1)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, actionDate=suspension_date, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )

        response = client.with_token(user).post("/native/v1/account/unsuspend")
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
            current_time = date_utils.get_naive_utc_now()
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


class SuspendAccountForHackSuspicionTest:
    def test_suspend_account_for_suspicious_login(self, client):
        booking = booking_factories.BookingFactory()
        user = booking.user

        response = client.with_token(user).post("/native/v1/account/suspend_for_hack_suspicion")

        assert response.status_code == 204
        assert booking.status == BookingStatus.CANCELLED
        db.session.refresh(user)
        assert not user.isActive
        assert user.suspension_reason == users_constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER
        assert user.suspension_date
        assert len(user.suspension_action_history) == 1
        assert user.suspension_action_history[0].userId == user.id
        assert user.suspension_action_history[0].authorUserId == user.id


class AnonymizeUserTest:
    @pytest.mark.parametrize(
        "roles",
        [
            [users_models.UserRole.UNDERAGE_BENEFICIARY],
            [users_models.UserRole.BENEFICIARY],
            [],
        ],
    )
    def test_anonymize_ex_beneficiary(self, client, roles):
        user = users_factories.BeneficiaryFactory(validatedBirthDate=date(2000, 1, 1), roles=roles)

        response = client.with_token(user).post("/native/v1/account/anonymize")

        assert response.status_code == 204
        assert not user.isActive
        assert db.session.query(users_models.GdprUserAnonymization).filter_by(userId=user.id).count() == 1

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.BENEFICIARY_PRE_ANONYMIZATION.value
        )

    def test_no_deposit(self, client):
        user = users_factories.UserFactory(age=16)

        response = client.with_token(user).post("/native/v1/account/anonymize")

        assert response.status_code == 204
        assert not user.isActive
        assert db.session.query(users_models.GdprUserAnonymization).filter_by(userId=user.id).count() == 1

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.BENEFICIARY_PRE_ANONYMIZATION.value
        )

    def test_pending_gdpr_extract(self, client):
        user = users_factories.BeneficiaryFactory(validatedBirthDate=date(2000, 1, 1))
        users_factories.GdprUserDataExtractBeneficiaryFactory(user=user)

        response = client.with_token(user).post("/native/v1/account/anonymize")

        assert response.status_code == 400
        assert response.json["code"] == "EXISTING_UNPROCESSED_GDPR_EXTRACT"
        assert user.isActive
        assert not mails_testing.outbox

    @pytest.mark.parametrize(
        "role",
        [
            users_models.UserRole.PRO,
            users_models.UserRole.NON_ATTACHED_PRO,
            users_models.UserRole.ANONYMIZED,
            users_models.UserRole.ADMIN,
        ],
    )
    def test_not_anonymizable_role(self, client, role):
        user = users_factories.BeneficiaryFactory(validatedBirthDate=date(2000, 1, 1), roles=[role])

        response = client.with_token(user).post("/native/v1/account/anonymize")

        assert response.status_code == 400
        assert response.json["code"] == "NOT_ANONYMIZABLE_BENEFICIARY"
        assert user.isActive
        assert not mails_testing.outbox

    def test_active_beneficiary(self, client):
        user = users_factories.BeneficiaryFactory()

        response = client.with_token(user).post("/native/v1/account/anonymize")

        assert response.status_code == 400
        assert response.json["code"] == "NOT_ANONYMIZABLE_BENEFICIARY"
        assert user.isActive
        assert not mails_testing.outbox

    def test_pending_anonymization(self, client):
        user = users_factories.BeneficiaryFactory(validatedBirthDate=date(2000, 1, 1))
        users_factories.GdprUserAnonymizationFactory(user=user)

        response = client.with_token(user).post("/native/v1/account/anonymize")

        assert response.status_code == 400
        assert response.json["code"] == "ALREADY_HAS_PENDING_ANONYMIZATION"
        assert user.isActive
        assert not mails_testing.outbox
