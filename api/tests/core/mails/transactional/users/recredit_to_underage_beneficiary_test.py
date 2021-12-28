import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.users.recredit_to_underage_beneficiary import (
    get_recredit_to_underage_beneficiary_email_data,
)
from pcapi.core.mails.transactional.users.recredit_to_underage_beneficiary import (
    send_recredit_email_to_underage_beneficiary,
)
from pcapi.core.payments.api import get_granted_deposit
from pcapi.core.testing import override_features
from pcapi.core.users.api import get_domains_credit
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class SendinblueSendNewlyEligibleUserEmailTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_send_recredit_email_to_underage_beneficiary(self):
        # given
        user = users_factories.UnderageBeneficiaryFactory()

        # when
        send_recredit_email_to_underage_beneficiary(user)

        # then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["template"] == {
            "id_prod": 303,
            "id_not_prod": 31,
            "tags": ["anniversaire_16_17_ans"],
            "use_priority_queue": False,
        }

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_return_correct_recredit_email_to_underage_beneficiary_email_data_16yo(
        self,
    ):
        # given
        user = users_factories.UnderageBeneficiaryFactory(subscription_age=16)
        granted_deposit = get_granted_deposit(user, user.eligibility)
        domains_credit = get_domains_credit(user)

        # when
        data = get_recredit_to_underage_beneficiary_email_data(user)

        # then
        assert data.params["FIRSTNAME"] == user.firstName
        assert data.params["NEW_CREDIT"] == granted_deposit.amount
        assert data.params["CREDIT"] == domains_credit.all.remaining

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_return_correct_recredit_email_to_underage_beneficiary_email_data_17yo(
        self,
    ):
        # given
        user = users_factories.UnderageBeneficiaryFactory(subscription_age=17)
        granted_deposit = get_granted_deposit(user, user.eligibility)
        domains_credit = get_domains_credit(user)

        # when
        data = get_recredit_to_underage_beneficiary_email_data(user)

        # then
        assert data.params["FIRSTNAME"] == user.firstName
        assert data.params["NEW_CREDIT"] == granted_deposit.amount
        assert data.params["CREDIT"] == domains_credit.all.remaining
