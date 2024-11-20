from unittest.mock import patch

import pytest

from pcapi import settings

from tests.test_utils import run_command


@pytest.mark.usefixtures("clean_database")
def test_sync_instructor_ids(app):
    with patch("pcapi.core.users.ds.sync_instructor_ids") as mock_ds:
        run_command(app, "sync_instructor_ids")

    mock_ds.assert_called_once_with(int(settings.DS_USER_ACCOUNT_UPDATE_PROCEDURE_ID))
