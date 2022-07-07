import logging

from pcapi.core.permissions import api as perm_api
from pcapi.core.permissions import models as perm_models
from pcapi.core.permissions import utils as perm_utils
from pcapi.models.api_errors import ApiErrors
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from . import serialization


logger = logging.getLogger(__name__)


@blueprint.backoffice_blueprint.route("roles", methods=["GET"])
@spectree_serialize(
    response_model=serialization.ListRoleResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.MANAGE_PERMISSIONS)
def list_roles() -> serialization.ListRoleResponseModel:
    roles = perm_api.list_roles()
    return serialization.ListRoleResponseModel(
        roles=[
            serialization.Role(
                id=role.id,
                name=role.name,
                permissions=[
                    serialization.Permission(
                        id=perm.id, name=perm_models.Permissions[perm.name].value, category=perm.category
                    )
                    for perm in role.permissions
                ],
            )
            for role in roles
        ]
    )


@blueprint.backoffice_blueprint.route("permissions", methods=["GET"])
@spectree_serialize(
    response_model=serialization.ListPermissionResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.MANAGE_PERMISSIONS)
def list_permissions() -> serialization.ListPermissionResponseModel:
    permissions = perm_api.list_permissions()
    return serialization.ListPermissionResponseModel(
        permissions=[
            serialization.Permission(id=perm.id, name=perm_models.Permissions[perm.name].value, category=perm.category)  # type: ignore [misc]
            for perm in permissions
        ]
    )


@blueprint.backoffice_blueprint.route("roles", methods=["POST"])
@spectree_serialize(
    response_model=serialization.Role,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.MANAGE_PERMISSIONS)
def create_role(body: serialization.RoleRequestModel) -> serialization.Role:
    new_role = perm_api.create_role(name=body.name, permission_ids=body.permissionIds)
    return serialization.Role(
        id=new_role.id,
        name=new_role.name,
        permissions=[
            serialization.Permission(id=perm.id, name=perm_models.Permissions[perm.name].value, category=perm.category)
            for perm in new_role.permissions
        ],
    )


@blueprint.backoffice_blueprint.route("roles/<int:id_>", methods=["PUT"])
@spectree_serialize(
    response_model=serialization.Role,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.MANAGE_PERMISSIONS)
def update_role(id_: int, body: serialization.RoleRequestModel) -> serialization.Role:
    updated_role = perm_api.update_role(id_=id_, name=body.name, permission_ids=body.permissionIds)
    return serialization.Role.from_orm(updated_role)


@blueprint.backoffice_blueprint.route("roles/<int:id_>", methods=["DELETE"])
@spectree_serialize(
    response_model=serialization.Role,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.MANAGE_PERMISSIONS)
def delete_role(id_: int) -> serialization.Role:
    try:
        deleted_id, deleted_name, deleted_permissions = perm_api.delete_role(id_=id_)
    except ValueError as err:
        raise ApiErrors(errors={"id": str(err)})

    return serialization.Role(id=deleted_id, name=deleted_name, permissions=deleted_permissions)
