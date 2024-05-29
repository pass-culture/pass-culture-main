import click

import pcapi.connectors.dms.api as dms_connector_api
import pcapi.core.subscription.api as subscription_api
import pcapi.core.subscription.dms.api as dms_api
import pcapi.core.users.models as users_models
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("import_dms_application")
@click.argument("application_number", type=int, required=True)
def import_dms_application(application_number: int) -> None:
    dms_application = dms_connector_api.DMSGraphQLClient().get_single_application_details(application_number)
    dms_api.handle_dms_application(dms_application)


@blueprint.cli.command("activate_user")
@click.argument("user_id", type=int, required=True)
def activate_user(user_id: int) -> None:
    user = users_models.User.query.filter_by(id=user_id).one_or_none()
    if user is None:
        raise ValueError(f"User {user_id} not found")
    subscription_api.activate_beneficiary_if_no_missing_step(user)
