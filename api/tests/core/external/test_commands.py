from unittest.mock import patch

import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.core.users import testing

from tests.test_utils import run_command


@pytest.mark.usefixtures("clean_database")
def test_update_sendinblue_batch_users(app):
    users_factories.BeneficiaryGrant18Factory.create_batch(2)

    with patch(
        "pcapi.core.external.sendinblue.brevo_python.api.contacts_api.ContactsApi.import_contacts"
    ) as mock_import_contacts:
        result = run_command(app, "update_sendinblue_batch_users", "--sync-sendinblue")

    mock_import_contacts.assert_called_once()

    assert "2 users formatted for sendinblue..." in result.stdout
    assert "Exception" not in result.stdout


@pytest.mark.usefixtures("clean_database")
def test_update_sendinblue_pro(app):
    users_factories.UserFactory()  # excluded
    users_factories.AdminFactory()  # excluded
    offerers_factories.UserOffererFactory(user__email="first@example.com")
    offerers_factories.UserOffererFactory(user__email="second@example.com")
    offerers_factories.VenueFactory(bookingEmail="third@example.com")
    offerers_factories.UserNotValidatedOffererFactory(user__email="fourth@example.com")

    result = run_command(app, "update_sendinblue_pro")

    assert len(testing.sendinblue_requests) == 4
    assert {request["email"] for request in testing.sendinblue_requests} == {
        "first@example.com",
        "second@example.com",
        "third@example.com",
        "fourth@example.com",
    }

    assert "Exception" not in result.stdout
