import json
from unittest import mock

import pytest

from pcapi.core import testing
from pcapi.core.users.models import User
from pcapi.scripts.backoffice_users.create_backoffice_users import create_backoffice_users_from_google_group


google_response = ' \
{ \
  "kind": "admin#directory#members", \
   "members": [ \
   { \
    "kind": "admin#directory#members", \
    "id": "group member\'s unique ID", \
    "email": "some-group@example.com", \
    "role": "MANAGER", \
    "type": "GROUP" \
   }, \
   { \
    "kind": "admin#directory#members", \
    "id": "group member\'s unique ID", \
    "email": "john.doe@example.com", \
    "role": "MANAGER", \
    "type": "USER" \
   } \
  ], \
   "nextPageToken": "NNNNN" \
}'


class RunTest:
    @pytest.mark.usefixtures("db_session")
    @mock.patch("pcapi.scripts.backoffice_users.create_backoffice_users.get_google_workspace_group_members")
    @testing.override_settings(BACKOFFICE_ALLOW_USER_CREATION=True)
    def test_should_do_create_users(
        self,
        get_google_workspace_group_members,
    ):
        # given
        google_group_address = "dev@example.com"
        get_google_workspace_group_members.return_value = json.loads(google_response)

        # when
        create_backoffice_users_from_google_group(google_group_address)

        # then
        get_google_workspace_group_members.assert_called_once_with(google_group_address)

        user_created = User.query.filter_by(email="john.doe@example.com").one()
        assert user_created is not None

        group_user_not_created = User.query.filter_by(email="some-group@example.com").one_or_none()
        assert group_user_not_created is None
