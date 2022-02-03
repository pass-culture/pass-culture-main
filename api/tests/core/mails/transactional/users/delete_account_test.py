import dataclasses

import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.delete_account import get_user_request_to_delete_account_email_data
from pcapi.core.mails.transactional.users.delete_account import send_user_request_to_delete_account_reception_email
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class UserRequestDeleteAccountReceptionEmailTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_get_email_metadata(self):
        # Given
        user = users_factories.UserFactory.build(email="fabien+test@example.net", firstName="Fabien")

        # When
        data = get_user_request_to_delete_account_email_data(user)

        # Then
        assert data.template == TransactionalEmail.USER_REQUEST_DELETE_ACCOUNT_RECEPTION.value
        assert data.params["FIRSTNAME"] == "Fabien"

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_send_correct_mail(self):
        # Given
        user = users_factories.UserFactory.build(email="fabien+test@example.net", firstName="Fabien")
        # When
        send_user_request_to_delete_account_reception_email(user)

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.USER_REQUEST_DELETE_ACCOUNT_RECEPTION.value
        )
        assert mails_testing.outbox[0].sent_data["To"] == "fabien+test@example.net"
        assert mails_testing.outbox[0].sent_data["params"] == {"FIRSTNAME": user.firstName}
