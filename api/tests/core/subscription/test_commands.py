import unittest

from pcapi.connectors.big_query.queries import UserThatLandedOnComeBackLaterModel
import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
from pcapi.core.subscription.commands import _send_notification_to_users_that_landed_on_come_back_later
import pcapi.core.users.factories as users_factories
import pcapi.notifications.push as push_notifications
from pcapi.notifications.push import testing


class SendRemindersTest:
    @unittest.mock.patch(
        "pcapi.connectors.big_query.queries.UsersThatLandedOnComeBackLater.execute",
        return_value=[
            UserThatLandedOnComeBackLaterModel(user_id=1, event_date="2021-01-01"),
            UserThatLandedOnComeBackLaterModel(user_id=2, event_date="2021-01-01"),
        ],
    )
    def test_reminders_to_users_that_landed_on_come_back_later(self, mock_execute):
        _send_notification_to_users_that_landed_on_come_back_later()

        assert testing.requests == [
            {
                "user_ids": [1, 2],
                "event_name": push_notifications.BatchEvent.USER_LANDED_ON_COME_BACK_LATER_PAGE.value,
                "event_payload": {"days_ago": 3},
                "can_be_asynchronously_retried": True,
            }
        ]

    @unittest.mock.patch(
        "pcapi.connectors.big_query.queries.UsersThatLandedOnComeBackLater.execute",
        return_value=[
            UserThatLandedOnComeBackLaterModel(user_id=1, event_date="2021-01-01"),
            UserThatLandedOnComeBackLaterModel(user_id=2, event_date="2021-01-01"),
        ],
    )
    def should_filter_out_users_that_have_an_identity_fraud_check_after_the_event_date(self, mock_execute):
        user1 = users_factories.UserFactory(id=1)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user1, type=fraud_models.FraudCheckType.UBBLE, dateCreated="2021-01-02"
        )

        _send_notification_to_users_that_landed_on_come_back_later()

        assert testing.requests == [
            {
                "user_ids": [2],
                "event_name": push_notifications.BatchEvent.USER_LANDED_ON_COME_BACK_LATER_PAGE.value,
                "event_payload": {"days_ago": 3},
                "can_be_asynchronously_retried": True,
            }
        ]
