import pytest

from pcapi.notifications.push import testing as push_testing
from pcapi.notifications.push import update_user_attributes


pytestmark = pytest.mark.usefixtures("db_session")


def test_update_user_attributes():
    user_id = 123
    attributes = {"param": "value"}

    update_user_attributes(user_id, attributes)

    assert push_testing.requests == [{"attribute_values": {"param": "value"}, "user_id": 123}]
