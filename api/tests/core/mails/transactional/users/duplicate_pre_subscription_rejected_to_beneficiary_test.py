from dataclasses import asdict
from unittest.mock import patch

import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.subscription.factories import BeneficiaryPreSubscriptionFactory
from pcapi.core.testing import override_features
from pcapi.domain.user_emails import send_rejection_email_to_beneficiary_pre_subscription


pytestmark = pytest.mark.usefixtures("db_session")


class MailjetSendRejectionEmailToBeneficiaryPreSubscriptionTest:
    @patch(
        "pcapi.core.mails.transactional.users.email_duplicate_pre_subscription_rejected.get_duplicate_beneficiary_pre_subscription_rejected_data",
        return_value={"MJ-TemplateID": 1530996},
    )
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def when_beneficiary_is_a_duplicate_sends_correct_template(self, mocked_make_data) -> None:
        # given
        beneficiary_pre_subscription = BeneficiaryPreSubscriptionFactory()

        # when
        send_rejection_email_to_beneficiary_pre_subscription(beneficiary_pre_subscription, beneficiary_is_eligible=True)

        # then
        mocked_make_data.assert_called_once()
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 1530996

    @patch(
        "pcapi.core.mails.transactional.users.email_duplicate_pre_subscription_rejected.get_not_eligible_beneficiary_pre_subscription_rejected_data",
        return_value={"MJ-TemplateID": 1619528},
    )
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def when_beneficiary_is_not_eligible_sends_correct_template(self, mocked_make_data) -> None:
        # given
        beneficiary_pre_subscription = BeneficiaryPreSubscriptionFactory()

        # when
        send_rejection_email_to_beneficiary_pre_subscription(
            beneficiary_pre_subscription, beneficiary_is_eligible=False
        )

        # then
        mocked_make_data.assert_called_once()
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 1619528


class SendinblueSendRejectionEmailToBeneficiaryPreSubscriptionTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def when_beneficiary_is_a_duplicate_sends_correct_template_sendinblue(self) -> None:
        # given
        beneficiary_pre_subscription = BeneficiaryPreSubscriptionFactory()

        # when
        send_rejection_email_to_beneficiary_pre_subscription(beneficiary_pre_subscription, beneficiary_is_eligible=True)

        # then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["template"] == asdict(
            TransactionalEmail.EMAIL_DUPLICATE_BENEFICIARY_PRE_SUBCRIPTION_REJECTED.value
        )

    @patch(
        "pcapi.core.mails.transactional.users.email_duplicate_pre_subscription_rejected.get_not_eligible_beneficiary_pre_subscription_rejected_data",
        return_value={"MJ-TemplateID": 1619528},  # currently no sendinblue equivalent email
    )
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def when_beneficiary_is_not_eligible_sends_correct_template_sendinblue(self, mocked_make_data) -> None:
        # given
        beneficiary_pre_subscription = BeneficiaryPreSubscriptionFactory()

        # when
        send_rejection_email_to_beneficiary_pre_subscription(
            beneficiary_pre_subscription, beneficiary_is_eligible=False
        )

        # then
        mocked_make_data.assert_called_once()
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 1619528
