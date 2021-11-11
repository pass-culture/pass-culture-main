import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.users import factories as users_factories
from pcapi.scripts.beneficiary import send_dms_application_emails


pytestmark = pytest.mark.usefixtures("db_session")


class SendDMSApplicationEMailsTest:
    def test_run(self):
        """
        Test that only the expected users are returned.

        Create a context with an extra user and an extra BeneficiaryImport and
        ensure that only those related are the one that are used and receiving
        an email.
        """
        users_factories.UserFactory()
        users_factories.BeneficiaryImportFactory(source="some source")
        beneficiary_imports = users_factories.BeneficiaryImportFactory.create_batch(3, source="source")

        expected_users = sorted([bi.beneficiary for bi in beneficiary_imports], key=lambda x: x.id)
        expected_email_dst = {user.email for user in expected_users}

        application_ids = [bi.applicationId for bi in beneficiary_imports]

        users = send_dms_application_emails.run(application_ids, "source")
        users = sorted(users, key=lambda x: x.id)

        assert users == expected_users
        assert len(mails_testing.outbox) == 1

        email = mails_testing.outbox[0]
        email_dst = {email.strip() for email in email.sent_data["To"].split(",")}
        assert email_dst == expected_email_dst
