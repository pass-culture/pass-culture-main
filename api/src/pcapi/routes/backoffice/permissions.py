import logging

from pcapi.core.permissions import api as perm_api
from pcapi.core.permissions import models as perm_models
from pcapi.core.permissions import utils as perm_utils
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from .serialization import ListRoleResponseModel
from .serialization import Role


logger = logging.getLogger(__name__)


@blueprint.backoffice_blueprint.route("/roles")
@perm_utils.permission_required(perm_models.Permissions.MANAGE_PERMISSIONS)
@spectree_serialize(
    response_model=ListRoleResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
def list_roles() -> ListRoleResponseModel:
    roles = perm_api.list_roles()
    return ListRoleResponseModel(roles=[Role.from_orm(role) for role in roles])
