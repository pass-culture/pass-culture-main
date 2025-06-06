import pytest

import pcapi.core.users.factories as users_factories
from pcapi.core.fraud.phone_validation import sending_limit


pytestmark = pytest.mark.usefixtures("db_session")


def test_get_remaining_sms_sending_attempts(app):
    user = users_factories.UserFactory()
    app.redis_client.set(f"sent_SMS_counter_user_{user.id}", 0)

    assert sending_limit.get_remaining_sms_sending_attempts(app.redis_client, user) == 3

    sending_limit.update_sent_SMS_counter(app.redis_client, user)
    sending_limit.update_sent_SMS_counter(app.redis_client, user)

    assert sending_limit.get_remaining_sms_sending_attempts(app.redis_client, user) == 1

    sending_limit.update_sent_SMS_counter(app.redis_client, user)
    sending_limit.update_sent_SMS_counter(app.redis_client, user)

    # test that remaining attempts don't go under 0
    assert sending_limit.get_remaining_sms_sending_attempts(app.redis_client, user) == 0


def test_get_attempt_limitation_expiration_time(app):
    user = users_factories.UserFactory()

    assert sending_limit.get_attempt_limitation_expiration_time(app.redis_client, user) is None

    sending_limit.update_sent_SMS_counter(app.redis_client, user)

    assert sending_limit.get_attempt_limitation_expiration_time(app.redis_client, user) is not None


@pytest.mark.settings(MAX_PHONE_VALIDATION_ATTEMPTS=1)
def test_get_code_validation_attempts(app):
    user = users_factories.UserFactory()

    assert sending_limit.get_code_validation_attempts(app.redis_client, user).attempts == 0
    assert sending_limit.get_code_validation_attempts(app.redis_client, user).remaining == 1
