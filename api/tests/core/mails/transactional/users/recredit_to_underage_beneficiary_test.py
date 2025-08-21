import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.recredit_to_underage_beneficiary import (
    get_recredit_to_underage_beneficiary_email_data,
)
from pcapi.core.mails.transactional.users.recredit_to_underage_beneficiary import (
    send_recredit_email_to_underage_beneficiary,
)
from pcapi.core.users import factories as users_factories
from pcapi.core.users.api import get_domains_credit


pytestmark = pytest.mark.usefixtures("db_session")


class SendinblueSendNewlyEligibleUserEmailTest:
    def test_send_recredit_email_to_underage_beneficiary(self):
        # given
        user = users_factories.UnderageBeneficiaryFactory()
        domains_credit = get_domains_credit(user)
        recredit_amount = 30

        # when
        send_recredit_email_to_underage_beneficiary(user, recredit_amount, domains_credit)

        # then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0]["template"] == TransactionalEmail.RECREDIT_TO_UNDERAGE_BENEFICIARY.value.__dict__

    def test_return_correct_recredit_email_to_underage_beneficiary_email_data(
        self,
    ):
        # given
        user = users_factories.UnderageBeneficiaryFactory(subscription_age=16)
        domains_credit = get_domains_credit(user)
        recredit_amount = 30

        # when
        data = get_recredit_to_underage_beneficiary_email_data(user, recredit_amount, domains_credit)

        # then
        assert data.params["FIRSTNAME"] == user.firstName
        assert data.params["NEW_CREDIT"] == recredit_amount
        assert data.params["FORMATTED_NEW_CREDIT"] == "30 €"
        assert data.params["CREDIT"] == 30
        assert data.params["FORMATTED_CREDIT"] == "30 €"

    def test_return_formatted_credit_for_caledonian_user(self):
        # given
        user = users_factories.UnderageBeneficiaryFactory(subscription_age=16, postalCode="98818")
        bookings_factories.BookingFactory(user=user, stock__price=30)
        domains_credit = get_domains_credit(user)
        recredit_amount = 30

        # when
        data = get_recredit_to_underage_beneficiary_email_data(user, recredit_amount, domains_credit)

        # then
        assert data.params["FIRSTNAME"] == user.firstName
        assert data.params["NEW_CREDIT"] == recredit_amount
        assert data.params["FORMATTED_NEW_CREDIT"] == "3580 F"
        assert data.params["CREDIT"] == 0
        assert data.params["FORMATTED_CREDIT"] == "0 F"
