import logging

from pcapi.core.permissions import api as perm_api
from pcapi.core.permissions import models as perm_models
from pcapi.core.permissions import utils as perm_utils
from pcapi.models.api_errors import ApiErrors
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from .serialization import ListPermissionResponseModel
from .serialization import ListRoleResponseModel
from .serialization import Permission
from .serialization import Role
from .serialization import RoleRequestModel


logger = logging.getLogger(__name__)


@blueprint.backoffice_blueprint.route("roles", methods=["GET"])
@perm_utils.permission_required(perm_models.Permissions.MANAGE_PERMISSIONS)
@spectree_serialize(
    response_model=ListRoleResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
def list_roles() -> ListRoleResponseModel:
    roles = perm_api.list_roles()
    return ListRoleResponseModel(roles=[Role.from_orm(role) for role in roles])


@blueprint.backoffice_blueprint.route("permissions", methods=["GET"])
@perm_utils.permission_required(perm_models.Permissions.MANAGE_PERMISSIONS)
@spectree_serialize(
    response_model=ListPermissionResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
def list_permissions() -> ListPermissionResponseModel:
    permissions = perm_api.list_permissions()
    return ListPermissionResponseModel(
        permissions=[
            Permission(id=perm.id, name=perm_models.Permissions[perm.name].value, category=perm.category)
            for perm in permissions
        ]
    )


@blueprint.backoffice_blueprint.route("roles", methods=["POST"])
@perm_utils.permission_required(perm_models.Permissions.MANAGE_PERMISSIONS)
@spectree_serialize(
    response_model=Role,
    on_success_status=200,
    api=blueprint.api,
)
def create_role(body: RoleRequestModel) -> Role:
    new_role = perm_api.create_role(name=body.name, permission_ids=body.permissionIds)
    return Role.from_orm(new_role)


@blueprint.backoffice_blueprint.route("roles/<int:id_>", methods=["PUT"])
@perm_utils.permission_required(perm_models.Permissions.MANAGE_PERMISSIONS)
@spectree_serialize(
    response_model=Role,
    on_success_status=200,
    api=blueprint.api,
)
def update_role(id_: int, body: RoleRequestModel) -> Role:
    updated_role = perm_api.update_role(id_=id_, name=body.name, permission_ids=body.permissionIds)
    return Role.from_orm(updated_role)


@blueprint.backoffice_blueprint.route("roles/<int:id_>", methods=["DELETE"])
@perm_utils.permission_required(perm_models.Permissions.MANAGE_PERMISSIONS)
@spectree_serialize(
    on_success_status=204,
    api=blueprint.api,
)
def delete_role(id_: int) -> None:
    try:
        perm_api.delete_role(id_=id_)
    except ValueError as err:
        raise ApiErrors(errors={"id": str(err)})
