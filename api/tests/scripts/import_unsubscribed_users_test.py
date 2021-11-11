from unittest.mock import patch

import pytest

from pcapi.core.users.factories import UserFactory
from pcapi.scripts.import_unsubscribed_users import synchronize_unsubscribed_users


@pytest.mark.usefixtures("db_session")
class ImportunsubscribedUsersTest:
    @patch("pcapi.scripts.import_unsubscribed_users.import_contacts_in_sendinblue")
    @patch("pcapi.scripts.import_unsubscribed_users.format_sendinblue_users")
    @patch("pcapi.scripts.import_unsubscribed_users._get_emails")
    def test_synchronize_unsubscribed_users(self, _get_emails, format_sendinblue_users, import_contacts_in_sendinblue):
        default_notification_subscriptions_value = {"marketing_push": True, "marketing_email": True}
        updated_notification_subscriptions_value = {"marketing_push": True, "marketing_email": False}

        user_nominal = UserFactory(notificationSubscriptions=default_notification_subscriptions_value)
        user_control = UserFactory(notificationSubscriptions=default_notification_subscriptions_value)
        user_null_value = UserFactory()
        user_null_value.notificationSubscriptions = None
        user_empty_value = UserFactory(notificationSubscriptions={})
        user_somewhat_empty_value = UserFactory(notificationSubscriptions={"marketing_push": True})

        users_to_import = [
            user_nominal.email,
            user_null_value.email,
            user_empty_value.email,
            user_somewhat_empty_value.email,
            "missing_user@email.com",
        ]
        _get_emails.return_value = users_to_import

        synchronize_unsubscribed_users()

        assert user_control.notificationSubscriptions == default_notification_subscriptions_value
        assert user_nominal.notificationSubscriptions == updated_notification_subscriptions_value
        assert user_null_value.notificationSubscriptions == {"marketing_email": False}
        assert user_empty_value.notificationSubscriptions == {"marketing_email": False}
        assert user_somewhat_empty_value.notificationSubscriptions == updated_notification_subscriptions_value

        format_sendinblue_users.assert_called_once()
        import_contacts_in_sendinblue.assert_called_once()
