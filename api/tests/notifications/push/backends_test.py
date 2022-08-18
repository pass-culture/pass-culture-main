import pytest

from pcapi.notifications.push import testing as push_testing
from pcapi.notifications.push import update_user_attributes
from pcapi.notifications.push.backends.batch import BatchAPI


pytestmark = pytest.mark.usefixtures("db_session")


def test_update_user_attributes():
    user_id = 123
    attributes = {"param": "value"}

    update_user_attributes(BatchAPI.IOS, user_id, attributes)

    assert push_testing.requests == [
        {
            "attribute_values": {"param": "value"},
            "batch_api": "IOS",
            "user_id": 123,
            "can_be_asynchronously_retried": False,
        }
    ]
