import datetime
from dataclasses import asdict

import pytest
from dateutil.relativedelta import relativedelta

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.pro import pre_anonymization
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories


pytestmark = pytest.mark.usefixtures("db_session")


class SendPreAnonymizationEmailToProTest:
    def test_send_mail(self):
        user_offerer = offerers_factories.DeletedUserOffererFactory(
            user__lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=-30),
        )

        pre_anonymization.send_pre_anonymization_email_to_pro(user_offerer.user)

        assert mails_testing.outbox[0]["To"] == user_offerer.user.email
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.PRO_PRE_ANONYMIZATION.value)
        assert mails_testing.outbox[0]["params"] == {}
