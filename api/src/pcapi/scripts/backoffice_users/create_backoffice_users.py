from datetime import datetime

import click
import google.auth
import googleapiclient.discovery

from pcapi import settings
from pcapi.core.auth.api import BACKOFFICE_SERVICE_ACCOUNT_SCOPES
from pcapi.core.auth.api import delegate_credentials
import pcapi.core.users.api as users_api
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint("create_backoffice_users", __name__)

# retrieve all users from a google workspace group using Google workspace Admin sdk API
# https://developers.google.com/admin-sdk/directory/v1/guides/manage-group-members#get_all_members
# details regarding mandatory scope :
# https://developers.google.com/admin-sdk/directory/v1/guides/authorizing
# details about request and response
# https://developers.google.com/admin-sdk/directory/reference/rest/v1/members/list
# details about Python API implementation
# https://googleapis.github.io/google-api-python-client/docs/dyn/admin_directory_v1.members.html

DEFAULT_GROUP_ADDRESS = "dev@passculture.app"


def get_google_workspace_group_members(workspace_group_address: str) -> dict:
    credentials, _ = google.auth.default()
    delegated_credentials = delegate_credentials(
        credentials, settings.BACKOFFICE_USER_EMAIL, BACKOFFICE_SERVICE_ACCOUNT_SCOPES
    )
    directory_service = googleapiclient.discovery.build("admin", "directory_v1", credentials=delegated_credentials)
    response = directory_service.members().list(groupKey=workspace_group_address).execute()
    return response


def create_backoffice_users_from_google_group(workspace_group_address: str | None) -> None:
    if not settings.BACKOFFICE_ALLOW_USER_CREATION:
        return

    if not workspace_group_address:
        workspace_group_address = DEFAULT_GROUP_ADDRESS

    response = get_google_workspace_group_members(workspace_group_address)
    for member in response.get("members", []):
        if member["type"] != "USER":
            continue

        users_api.create_account(
            email=member["email"],
            password="some-temporary-string",
            birthdate=datetime.fromisoformat("2000-01-01"),
        )


@blueprint.cli.command("create_backoffice_users")
@click.argument("group_address", type=str, required=False)
def create_backoffice_users_command(group_address: str | None) -> None:
    """Create back-office users for each member of a given google group."""

    if not group_address:
        group_address = DEFAULT_GROUP_ADDRESS

    create_backoffice_users_from_google_group(group_address)
