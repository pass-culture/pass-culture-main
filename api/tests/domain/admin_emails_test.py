import pytest

import pcapi.core.mails.testing as mails_testing
import pcapi.core.users.factories as users_factories
from pcapi.domain.admin_emails import send_suspended_fraudulent_users_email


@pytest.mark.usefixtures("db_session")
def test_send_suspended_fraudulent_users_email(app):
    admin = users_factories.UserFactory(email="admin@email.com")
    fraudulent_users = [users_factories.UserFactory()]
    nb_cancelled_bookings = 0

    send_suspended_fraudulent_users_email(fraudulent_users, nb_cancelled_bookings, admin.email)

    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["To"] == "admin@email.com"
    assert mails_testing.outbox[0].sent_data["subject"] == "Fraude : suspension des utilisateurs frauduleux par ids"
