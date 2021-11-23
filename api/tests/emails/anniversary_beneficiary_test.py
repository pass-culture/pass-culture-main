from datetime import datetime

from dateutil.relativedelta import relativedelta
import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.anniversary_beneficiary_email import get_anniversary_16_17_user_email_data
from pcapi.core.mails.transactional.users.anniversary_beneficiary_email import get_anniversary_18_user_email_data
from pcapi.core.mails.transactional.users.anniversary_beneficiary_email import send_newly_eligible_18_user_email
from pcapi.core.payments import models as payments_models
import pcapi.core.payments.conf as deposit_conf
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories
from pcapi.models import db
from pcapi.repository import transaction


pytestmark = pytest.mark.usefixtures("db_session")


class SendNewlyEligibleUserEmailMailjetTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def test_send_activation_email(self):
        # given
        user = users_factories.UserFactory(
            dateOfBirth=(datetime.now() - relativedelta(years=18, days=5)), departementCode="93"
        )

        # when
        send_newly_eligible_18_user_email(user)

        # then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 2030056
        assert (
            mails_testing.outbox[0].sent_data["Vars"]["nativeAppLink"][:118]
            == "https://passcultureapptestauto.page.link/?link=https%3A%2F%2F"
            "app-native.testing.internal-passculture.app%2Fid-check%3F"
        )
        assert "email" in mails_testing.outbox[0].sent_data["Vars"]["nativeAppLink"]
        assert mails_testing.outbox[0].sent_data["Vars"]["depositAmount"] == 300

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def test_return_correct_email_metadata(self):
        # given
        user = users_factories.UserFactory(
            dateOfBirth=(datetime.now() - relativedelta(years=18, days=5)), departementCode="93"
        )

        # when
        email_data = get_anniversary_18_user_email_data(user)

        # then
        assert email_data["Mj-TemplateID"] == 2030056
        assert email_data["Mj-TemplateLanguage"] == True
        assert email_data["Mj-trackclick"] == 1
        assert (
            email_data["Vars"]["nativeAppLink"][:118]
            == "https://passcultureapptestauto.page.link/?link=https%3A%2F%2Fapp-native.testing.internal-passculture.app%2Fid-check%3F"
        )
        assert email_data["Vars"]["depositAmount"] == 300


class SendNewlyEligibleUserEmailSendinblueTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_return_correct_anniversary_18_user_email_metadata(self):
        # given
        user = users_factories.UserFactory(
            dateOfBirth=(datetime.now() - relativedelta(years=18, days=5)), departementCode="93"
        )

        # when
        data = get_anniversary_18_user_email_data(user)

        # then
        assert data.template == TransactionalEmail.ANNIVERSARY_18_BENEFICIARY.value

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_return_correct_anniversary_16_17_user_email_metadata(self):
        # given
        user = users_factories.UnderageBeneficiaryFactory(
            dateOfBirth=(datetime.now() - relativedelta(years=16, days=5)), departementCode="93"
        )

        # when
        data = get_anniversary_16_17_user_email_data(user)

        # then
        assert data.template == TransactionalEmail.ANNIVERSARY_16_17_BENEFICIARY.value
        assert data.params["FIRSTNAME"] == "Jeanne"
        assert data.params["NEW_CREDIT"] == 30
        assert data.params["CREDIT"] == 30

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_return_correct_anniversary_16_17_user_email_total_credit_amount(self):
        # given
        user = users_factories.UnderageBeneficiaryFactory(
            dateOfBirth=(datetime.now() - relativedelta(years=16, days=5)), departementCode="93"
        )

        with transaction():
            recredit = payments_models.Recredit(
                deposit=user.deposit,
                amount=100,
                recreditType=deposit_conf.RECREDIT_TYPE_AGE_MAPPING[user.age],
            )
            recredit.deposit.amount += recredit.amount
            user.recreditAmountToShow = recredit.amount if recredit.amount > 0 else None

            db.session.add(user)
            db.session.add(recredit)

        # when
        data = get_anniversary_16_17_user_email_data(user)

        # then
        assert data.params["CREDIT"] == 130  # user total amount
