import logging

import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.users import factories as users_factories


LOREM_IPSUM = """Lorem ipsum dolor sit amet, consectetur adipiscing elit,
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."""


@pytest.mark.usefixtures("db_session")
class PostFeedbackTest:
    def test_post_feedback(self, client, caplog):
        user = users_factories.BeneficiaryFactory()
        bookings_factories.BookingFactory(user=user)

        with caplog.at_level(logging.INFO):
            response = client.with_token(user).post(
                "/native/v1/feedback",
                json={"feedback": LOREM_IPSUM},
            )

        assert response.status_code == 204
        assert caplog.records[0].extra == {
            "feedback": LOREM_IPSUM,
            "age": user.age,
            "status": "beneficiary",
            "firstDepositActivationDate": user.deposit.dateCreated,
            "bookings_count": 1,
            "analyticsSource": "app-native",
        }
        assert caplog.records[0].technical_message_id == "user_feedback"
