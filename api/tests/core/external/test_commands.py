from unittest.mock import patch

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.core.users import testing

from tests.conftest import clean_database
from tests.test_utils import run_command


@clean_database
def test_update_sendinblue_batch_users(app):
    users_factories.BeneficiaryGrant18Factory.create_batch(2)

    with patch(
        "pcapi.core.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.import_contacts"
    ) as mock_import_contacts:
        result = run_command(app, "update_sendinblue_batch_users", "--sync-sendinblue")

    mock_import_contacts.assert_called_once()

    assert "2 users formatted for sendinblue..." in result.stdout
    assert "Exception" not in result.stdout


@clean_database
def test_update_sendinblue_pro(app):
    offerers_factories.UserOffererFactory(user__email="first@example.com")
    offerers_factories.UserOffererFactory(user__email="second@example.com")
    offerers_factories.VenueFactory(bookingEmail="third@example.com")

    result = run_command(app, "update_sendinblue_pro")

    assert len(testing.sendinblue_requests) == 3
    assert {request["email"] for request in testing.sendinblue_requests} == {
        "first@example.com",
        "second@example.com",
        "third@example.com",
    }

    assert "Exception" not in result.stdout
