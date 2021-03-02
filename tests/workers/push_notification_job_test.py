from unittest.mock import patch

from pcapi.workers.push_notification_job import update_user_attributes


@patch("pcapi.workers.push_notification_job.batch_push_notification_client.update_user_attributes")
def test_calls_use_case(mocked_update_user_attributes):
    # Given
    user_id = 5
    attribute_values = {"good": "values"}

    # When
    update_user_attributes(user_id, attribute_values)

    # Then
    mocked_update_user_attributes.assert_called_once_with(user_id, attribute_values)
