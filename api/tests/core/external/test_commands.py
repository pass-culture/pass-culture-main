import logging
from unittest.mock import patch

import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.core.users import testing

from tests.test_utils import run_command


@pytest.mark.usefixtures("clean_database")
def test_update_brevo_and_batch_users(app, caplog):
    users_factories.BeneficiaryGrant18Factory.create_batch(2)

    with patch(
        "pcapi.core.external.sendinblue.brevo_python.api.contacts_api.ContactsApi.import_contacts"
    ) as mock_import_contacts:
        with patch(
            "pcapi.core.external.commands.update_brevo_batch_attributes.update_users_attributes"
        ) as mock_update_batch:
            with caplog.at_level(logging.INFO):
                run_command(app, "update_brevo_and_batch_users", "--sync-brevo", "--sync-batch")

        assert caplog.messages[0].startswith(
            "[update_brevo_and_batch_users] Update multiple user attributes in [Batch, Brevo] with user ids in range "
        )
        assert "[update_brevo_and_batch_users] 2 users formatted for Batch..." in caplog.messages
        assert "[update_brevo_and_batch_users] 2 users formatted for Brevo..." in caplog.messages
        assert "[update_brevo_and_batch_users] 2 users updated" in caplog.messages
        assert "Failed to collect user attributes" not in str(caplog.messages)

    mock_import_contacts.assert_called()
    mock_update_batch.assert_called()


@pytest.mark.usefixtures("clean_database")
def test_update_brevo_pro(app, caplog):
    users_factories.UserFactory()  # excluded
    users_factories.AdminFactory()  # excluded
    offerers_factories.UserOffererFactory(user__email="first@example.com")
    offerers_factories.UserOffererFactory(user__email="second@example.com")
    offerers_factories.VenueFactory(bookingEmail="third@example.com")
    offerers_factories.UserNotValidatedOffererFactory(user__email="fourth@example.com")

    with caplog.at_level(logging.INFO):
        result = run_command(app, "update_brevo_pro")

    assert len(testing.sendinblue_requests) == 4
    assert {request["email"] for request in testing.sendinblue_requests} == {
        "first@example.com",
        "second@example.com",
        "third@example.com",
        "fourth@example.com",
    }

    assert caplog.messages == [
        "[update_brevo_pro] 1 booking emails",
        "[update_brevo_pro] 3 pro users emails",
        "[update_brevo_pro] Total: 4 distinct emails",
        "[update_brevo_pro] 4 emails to process",
        "[update_brevo_pro] (1/4) first@example.com",
        "[update_brevo_pro] (2/4) fourth@example.com",
        "[update_brevo_pro] (3/4) second@example.com",
        "[update_brevo_pro] (4/4) third@example.com",
        "[update_brevo_pro] Completed with 0 errors",
    ]
    assert "Exception" not in result.stdout
