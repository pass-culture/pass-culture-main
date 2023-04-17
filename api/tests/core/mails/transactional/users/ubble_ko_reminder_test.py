import datetime

from dateutil.relativedelta import relativedelta
import pytest

import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
import pcapi.core.mails.testing as mails_testing
import pcapi.core.mails.transactional.sendinblue_template_ids as sendinblue_template
from pcapi.core.mails.transactional.users.ubble.reminder_emails import _find_users_to_remind
from pcapi.core.mails.transactional.users.ubble.reminder_emails import send_reminder_emails
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
import pcapi.notifications.push.testing as push_testing


def build_user_with_ko_retryable_ubble_fraud_check(
    user: users_models.User | None = None,
    user_age: int = 18,
    ubble_date_created: datetime.datetime = datetime.datetime.utcnow() - relativedelta(days=7),
    ubble_eligibility: users_models.EligibilityType = users_models.EligibilityType.AGE18,
    # pylint: disable=dangerous-default-value
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
        self.error_codes = [
            fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE,
            fraud_models.FraudReasonCode.ID_CHECK_DATA_MATCH,
            fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC,
            fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED,
            fraud_models.FraudReasonCode.ID_CHECK_EXPIRED,
        ]

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

    def should_find_users_when_they_had_ok_fraud_checks_of_another_eligibility(self):
        # Given
        user = build_user_with_ko_retryable_ubble_fraud_check()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
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

        assert result == [(user, [fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE])]


@pytest.mark.usefixtures("db_session")
class SendUbbleKoReminderEmailTest:
    @override_settings(DAYS_BEFORE_UBBLE_QUICK_ACTION_REMINDER=7)
    def should_send_email_to_users(self):
        # Given
        user1 = build_user_with_ko_retryable_ubble_fraud_check(
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC]
        )
        user2 = build_user_with_ko_retryable_ubble_fraud_check(
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE]
        )

        # When
        send_reminder_emails()

        # Then
        assert len(mails_testing.outbox) == 2
        assert mails_testing.outbox[0].sent_data["To"] == user1.email
        assert (
            mails_testing.outbox[0].sent_data["template"]
            == sendinblue_template.TransactionalEmail.UBBLE_KO_REMINDER_ID_CHECK_NOT_AUTHENTIC.value.__dict__
        )
        assert mails_testing.outbox[1].sent_data["To"] == user2.email
        assert (
            mails_testing.outbox[1].sent_data["template"]
            == sendinblue_template.TransactionalEmail.UBBLE_KO_REMINDER_ID_CHECK_UNPROCESSABLE.value.__dict__
        )

    @override_settings(DAYS_BEFORE_UBBLE_LONG_ACTION_REMINDER=21)
    def should_send_21_days_reminders(self):
        twenty_one_days_ago = datetime.datetime.utcnow() - relativedelta(days=21)
        user1 = build_user_with_ko_retryable_ubble_fraud_check(
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED], ubble_date_created=twenty_one_days_ago
        )
        user2 = build_user_with_ko_retryable_ubble_fraud_check(
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_EXPIRED], ubble_date_created=twenty_one_days_ago
        )

        send_reminder_emails()

        assert len(mails_testing.outbox) == 2

        user1_index = 0 if mails_testing.outbox[0].sent_data["To"] == user1.email else 1
        user2_index = 0 if mails_testing.outbox[0].sent_data["To"] == user2.email else 1

        assert (
            mails_testing.outbox[user1_index].sent_data["template"]
            == sendinblue_template.TransactionalEmail.UBBLE_KO_REMINDER_ID_CHECK_NOT_SUPPORTED.value.__dict__
        )

        assert (
            mails_testing.outbox[user2_index].sent_data["template"]
            == sendinblue_template.TransactionalEmail.UBBLE_KO_REMINDER_ID_CHECK_EXPIRED.value.__dict__
        )

    @override_settings(DAYS_BEFORE_UBBLE_LONG_ACTION_REMINDER=21)
    def should_notify_users_after_sending_an_email(self):
        twenty_one_days_ago = datetime.datetime.utcnow() - relativedelta(days=21)
        user1 = build_user_with_ko_retryable_ubble_fraud_check(
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED], ubble_date_created=twenty_one_days_ago
        )
        user2 = build_user_with_ko_retryable_ubble_fraud_check(
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_EXPIRED], ubble_date_created=twenty_one_days_ago
        )
        user3 = build_user_with_ko_retryable_ubble_fraud_check(
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED], ubble_date_created=twenty_one_days_ago
        )

        request1 = {
            "can_be_asynchronously_retried": True,
            "event_name": "has_ubble_ko_status",
            "event_payload": {"error_code": "id_check_not_supported"},
            "user_ids": [user1.id, user3.id],
        }
        request2 = {
            "can_be_asynchronously_retried": True,
            "event_name": "has_ubble_ko_status",
            "event_payload": {"error_code": "id_check_expired"},
            "user_ids": [user2.id],
        }

        send_reminder_emails()

        assert len(push_testing.requests) == 2
        assert request1 in push_testing.requests
        assert request2 in push_testing.requests
