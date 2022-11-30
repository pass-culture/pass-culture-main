import datetime

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core import testing
import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
import pcapi.core.mails.testing as mails_testing
import pcapi.core.mails.transactional.sendinblue_template_ids as sendinblue_template
from pcapi.core.mails.transactional.users.ubble.ubble_ko_reminder import _find_users_that_failed_ubble_check
from pcapi.core.mails.transactional.users.ubble.ubble_ko_reminder import send_ubble_ko_reminder_emails
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models


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

    def should_find_users_that_failed_ubble_check(self):
        # Given
        user = build_user_with_ko_retryable_ubble_fraud_check()

        # When
        found_user, _fraud_check = _find_users_that_failed_ubble_check(days_ago=7)[0]

        # Then
        assert found_user == user

    def should_not_find_users_that_failed_ubble_check_six_days_ago(self):
        # Given
        build_user_with_ko_retryable_ubble_fraud_check(
            ubble_date_created=datetime.datetime.utcnow() - relativedelta(days=6)
        )

        # When
        result = _find_users_that_failed_ubble_check(days_ago=7)

        # Then
        assert result == []

    def should_not_find_users_when_they_are_already_beneficiary(self):
        # Given
        user = users_factories.BeneficiaryGrant18Factory()
        build_user_with_ko_retryable_ubble_fraud_check(user=user)

        # When
        result = _find_users_that_failed_ubble_check(days_ago=7)

        # Then
        assert result == []

    def should_not_find_users_when_they_have_another_id_check_ok(self):
        # Given
        user = users_factories.UserFactory(dateOfBirth=self.eighteen_years_ago)
        build_user_with_ko_retryable_ubble_fraud_check(user=user)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.OK,
        )

        # When
        result = _find_users_that_failed_ubble_check(days_ago=7)

        # Then
        assert result == []

    def should_find_users_when_they_had_ok_fraud_checks_of_another_eligibility(self):
        # Given
        user = build_user_with_ko_retryable_ubble_fraud_check()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        print(_find_users_that_failed_ubble_check(days_ago=7))

        # When
        found_user, _fraud_check = _find_users_that_failed_ubble_check(days_ago=7)[0]

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
        )

        # When
        result = _find_users_that_failed_ubble_check(days_ago=7)

        # Then
        assert result == []

    def should_not_find_user_if_they_have_a_pending_id_check(self):
        # Given
        user = build_user_with_ko_retryable_ubble_fraud_check()
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.PENDING,
        )

        # When
        result = _find_users_that_failed_ubble_check(days_ago=7)

        # Then
        assert result == []


@pytest.mark.usefixtures("db_session")
class SendUbbleKoReminderEmailTest:
    @override_settings(UBBLE_KO_REMINDER_DELAY=7)
    def should_send_email_to_users(self):
        # Given
        user1 = build_user_with_ko_retryable_ubble_fraud_check()
        user2 = build_user_with_ko_retryable_ubble_fraud_check(
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE]
        )

        # When
        with testing.assert_num_queries(3):
            send_ubble_ko_reminder_emails()

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
