import datetime

import pytest
import time_machine
from dateutil.relativedelta import relativedelta

import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
import pcapi.core.fraud.ubble.constants as ubble_constants
import pcapi.core.mails.testing as mails_testing
import pcapi.core.mails.transactional.sendinblue_template_ids as sendinblue_template
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
import pcapi.notifications.push.testing as push_testing
from pcapi import settings
from pcapi.core.mails.transactional.users.ubble.reminder_emails import _find_users_to_remind
from pcapi.core.mails.transactional.users.ubble.reminder_emails import send_reminders
from pcapi.core.subscription.ubble import errors as ubble_errors


def build_user_with_ko_retryable_ubble_fraud_check(
    user: users_models.User | None = None,
    user_age: int = 18,
    ubble_date_created: datetime.datetime = datetime.datetime.utcnow() - relativedelta(days=7),
    ubble_eligibility: users_models.EligibilityType = users_models.EligibilityType.AGE17_18,
    reasonCodes: list[fraud_models.FraudReasonCode] = [fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC],
) -> users_models.User:
    """
    Generates a user and a fraud check with a retryable ubble status
    By default, the user is 18 years old and the fraud check is 7 days old
    If a user is provided, it will be used instead of generating a new one
    """
    if user is None:
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=user_age),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
    fraud_factories.BeneficiaryFraudCheckFactory(
        user=user,
        type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
        status=fraud_models.FraudCheckStatus.OK,
        eligibilityType=ubble_eligibility,
    )
    fraud_factories.BeneficiaryFraudCheckFactory(
        user=user,
        type=fraud_models.FraudCheckType.UBBLE,
        status=fraud_models.FraudCheckStatus.KO,
        reasonCodes=reasonCodes,
        dateCreated=ubble_date_created,
        eligibilityType=ubble_eligibility,
    )
    return user


@pytest.mark.usefixtures("db_session")
class FindUsersThatFailedUbbleTest:
    def setup_method(self):
        self.eighteen_years_ago = datetime.datetime.utcnow() - relativedelta(years=18)
        self.error_codes = (
            ubble_constants.REASON_CODES_FOR_QUICK_ACTION_REMINDERS
            + ubble_constants.REASON_CODES_FOR_LONG_ACTION_REMINDERS
        )

    def should_find_users_to_remind(self):
        # Given
        user = build_user_with_ko_retryable_ubble_fraud_check()

        # When
        found_user, _fraud_check = _find_users_to_remind(days_ago=7, reason_codes_filter=self.error_codes)[0]

        # Then
        assert found_user == user

    def should_not_find_users_to_remind(self):
        # Given
        build_user_with_ko_retryable_ubble_fraud_check(
            ubble_date_created=datetime.datetime.utcnow() - relativedelta(days=6)
        )

        # When
        result = _find_users_to_remind(days_ago=7, reason_codes_filter=self.error_codes)

        # Then
        assert not result

    def should_not_find_users_when_they_are_already_beneficiary(self):
        # Given
        user = users_factories.BeneficiaryGrant18Factory()
        build_user_with_ko_retryable_ubble_fraud_check(user=user)

        # When
        result = _find_users_to_remind(days_ago=7, reason_codes_filter=self.error_codes)

        # Then
        assert not result

    def should_not_find_users_when_they_have_another_id_check_ok(self):
        # Given
        user = build_user_with_ko_retryable_ubble_fraud_check(user_age=18)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.OK,
        )

        # When
        result = _find_users_to_remind(days_ago=7, reason_codes_filter=self.error_codes)

        # Then
        assert not result

    @pytest.mark.parametrize(
        "decree_month_offset",
        [
            pytest.param(-1, id="with eighteenth birthday before decree"),
            pytest.param(6, id="with decree between the seventeenth and eighteenth birthday"),
            pytest.param(13, id="with decree before seventeenth birthday"),
        ],
    )
    def should_find_users_when_they_had_ok_fraud_checks_of_another_eligibility(self, decree_month_offset):
        with time_machine.travel(settings.CREDIT_V3_DECREE_DATETIME + relativedelta(months=decree_month_offset)):
            # Given
            last_week = datetime.datetime.utcnow() - relativedelta(days=7)
            user = build_user_with_ko_retryable_ubble_fraud_check(ubble_date_created=last_week)
            year_when_user_was_underage = datetime.datetime.utcnow() - relativedelta(years=1)
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                status=fraud_models.FraudCheckStatus.OK,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
                dateCreated=year_when_user_was_underage,
            )

            # When
            found_user, _fraud_check = _find_users_to_remind(days_ago=7, reason_codes_filter=self.error_codes)[0]

            # Then
            assert found_user == user

    def should_not_find_user_if_they_already_retried_thrice(self):
        # Given
        user = build_user_with_ko_retryable_ubble_fraud_check()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.KO,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.KO,
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_DATA_MATCH],
        )

        # When
        result = _find_users_to_remind(days_ago=7, reason_codes_filter=self.error_codes)

        # Then
        assert not result

    def should_not_find_user_if_they_have_a_pending_id_check(self):
        # Given
        user = build_user_with_ko_retryable_ubble_fraud_check()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.PENDING,
        )

        # When
        result = _find_users_to_remind(days_ago=7, reason_codes_filter=self.error_codes)

        # Then
        assert not result

    def should_find_correct_reason_codes(self):
        user = build_user_with_ko_retryable_ubble_fraud_check(
            ubble_date_created=datetime.datetime.utcnow() - relativedelta(days=7)
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.KO,
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE],
            dateCreated=datetime.datetime.utcnow() - relativedelta(days=5),  # I want this one
        )

        result = _find_users_to_remind(days_ago=7, reason_codes_filter=self.error_codes)

        assert result == [(user, fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE)]


@pytest.mark.usefixtures("db_session")
class SendUbbleKoReminderReminderTest:
    def _are_requests_equal(self, request1: dict, request2: dict) -> bool:
        return (
            request1["can_be_asynchronously_retried"] == request2["can_be_asynchronously_retried"]
            and request1["event_name"] == request2["event_name"]
            and request1["event_payload"] == request2["event_payload"]
            and set(request1["user_ids"]) == set(request2["user_ids"])
        )

    @pytest.mark.settings(DAYS_BEFORE_UBBLE_QUICK_ACTION_REMINDER=7)
    def should_send_7_days_reminders(self):
        # Given
        user1 = build_user_with_ko_retryable_ubble_fraud_check(
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC]
        )
        user2 = build_user_with_ko_retryable_ubble_fraud_check(
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE]
        )

        # When
        send_reminders()

        # Then
        assert len(mails_testing.outbox) == 2
        assert {e["To"] for e in mails_testing.outbox} == {user1.email, user2.email}
        mail1 = [e for e in mails_testing.outbox if e["To"] == user1.email][0]
        assert (
            mail1["template"]
            == sendinblue_template.TransactionalEmail.UBBLE_KO_REMINDER_ID_CHECK_NOT_AUTHENTIC.value.__dict__
        )
        mail2 = [e for e in mails_testing.outbox if e["To"] == user2.email][0]
        assert (
            mail2["template"]
            == sendinblue_template.TransactionalEmail.UBBLE_KO_REMINDER_ID_CHECK_UNPROCESSABLE.value.__dict__
        )

    @pytest.mark.settings(DAYS_BEFORE_UBBLE_LONG_ACTION_REMINDER=21)
    def should_send_21_days_reminders(self):
        twenty_one_days_ago = datetime.datetime.utcnow() - relativedelta(days=21)
        user1 = build_user_with_ko_retryable_ubble_fraud_check(
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED], ubble_date_created=twenty_one_days_ago
        )
        user2 = build_user_with_ko_retryable_ubble_fraud_check(
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_EXPIRED], ubble_date_created=twenty_one_days_ago
        )

        send_reminders()

        assert len(mails_testing.outbox) == 2

        user1_index = 0 if mails_testing.outbox[0]["To"] == user1.email else 1
        user2_index = 0 if mails_testing.outbox[0]["To"] == user2.email else 1

        assert (
            mails_testing.outbox[user1_index]["template"]
            == sendinblue_template.TransactionalEmail.UBBLE_KO_REMINDER_ID_CHECK_NOT_SUPPORTED.value.__dict__
        )

        assert (
            mails_testing.outbox[user2_index]["template"]
            == sendinblue_template.TransactionalEmail.UBBLE_KO_REMINDER_ID_CHECK_EXPIRED.value.__dict__
        )

    @pytest.mark.settings(DAYS_BEFORE_UBBLE_QUICK_ACTION_REMINDER=7)
    @pytest.mark.parametrize(
        "reason_code",
        [
            fraud_models.FraudReasonCode.BLURRY_DOCUMENT_VIDEO,
            fraud_models.FraudReasonCode.DOCUMENT_DAMAGED,
            fraud_models.FraudReasonCode.LACK_OF_LUMINOSITY,
            fraud_models.FraudReasonCode.MISSING_REQUIRED_DATA,
            fraud_models.FraudReasonCode.NETWORK_CONNECTION_ISSUE,
            fraud_models.FraudReasonCode.NOT_DOCUMENT_OWNER,
            fraud_models.FraudReasonCode.UBBLE_INTERNAL_ERROR,
        ],
    )
    def should_send_default_email_to_user(self, reason_code):
        # Given
        user = build_user_with_ko_retryable_ubble_fraud_check(reasonCodes=[reason_code])

        # When
        send_reminders()

        # Then
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == user.email

    @pytest.mark.settings(DAYS_BEFORE_UBBLE_QUICK_ACTION_REMINDER=7)
    @pytest.mark.parametrize("reason_code", ubble_constants.REASON_CODES_FOR_QUICK_ACTION_REMINDERS)
    def should_send_email_for_quick_action_to_user(self, reason_code):
        # Given
        user = build_user_with_ko_retryable_ubble_fraud_check(reasonCodes=[reason_code])

        # When
        send_reminders()

        # Then
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == user.email

    @pytest.mark.settings(DAYS_BEFORE_UBBLE_LONG_ACTION_REMINDER=21)
    @pytest.mark.parametrize("reason_code", ubble_constants.REASON_CODES_FOR_LONG_ACTION_REMINDERS)
    def should_send_email_for_long_action_to_user(self, reason_code):
        # Given
        user = build_user_with_ko_retryable_ubble_fraud_check(
            reasonCodes=[reason_code], ubble_date_created=datetime.datetime.utcnow() - relativedelta(days=21)
        )

        # When
        send_reminders()

        # Then
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == user.email

    @pytest.mark.settings(DAYS_BEFORE_UBBLE_QUICK_ACTION_REMINDER=7)
    @pytest.mark.parametrize("reason_code", ubble_constants.REASON_CODES_FOR_QUICK_ACTION_REMINDERS)
    def should_send_email_for_most_relevant_error_to_user_for_quick_action(self, reason_code):
        # ID_CHECK_BLOCKED_OTHER is the least prioritized reason code
        other_reason_code = fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER

        # Given
        user = build_user_with_ko_retryable_ubble_fraud_check(reasonCodes=[reason_code, other_reason_code])

        # When
        send_reminders()

        # Then
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == user.email

    @pytest.mark.settings(DAYS_BEFORE_UBBLE_LONG_ACTION_REMINDER=21)
    @pytest.mark.parametrize("reason_code", ubble_constants.REASON_CODES_FOR_LONG_ACTION_REMINDERS)
    def should_send_reminder_for_most_relevant_error_to_user_for_long_action(self, reason_code):
        # ID_CHECK_BLOCKED_OTHER is the least prioritized reason code
        other_reason_code = fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER

        # Given
        user = build_user_with_ko_retryable_ubble_fraud_check(
            reasonCodes=[reason_code, other_reason_code],
            ubble_date_created=datetime.datetime.utcnow() - relativedelta(days=21),
        )

        # When
        send_reminders()

        # Then
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == user.email

    @pytest.mark.settings(DAYS_BEFORE_UBBLE_LONG_ACTION_REMINDER=7)
    @pytest.mark.parametrize(
        "reason_code",
        [
            reason_code
            for reason_code in ubble_constants.REASON_CODES_FOR_QUICK_ACTION_REMINDERS
            if ubble_errors.UBBLE_CODE_ERROR_MAPPING[reason_code].priority
            < ubble_errors.UBBLE_CODE_ERROR_MAPPING[fraud_models.FraudReasonCode.DUPLICATE_USER].priority
        ],
    )
    def should_not_send_email_if_most_relevant_is_not_retryable(self, reason_code):
        # DUPLICATE_USER is not retryable
        other_reason_code = fraud_models.FraudReasonCode.DUPLICATE_USER

        # Given
        build_user_with_ko_retryable_ubble_fraud_check(reasonCodes=[reason_code, other_reason_code])

        # When
        send_reminders()

        # Then
        assert not mails_testing.outbox
        assert not push_testing.requests
