import logging

from flask import Blueprint

from pcapi import settings
from pcapi.core.permissions.models import Permission
from pcapi.core.permissions.models import Permissions
from pcapi.core.permissions.models import Role
from pcapi.core.permissions.models import RolePermission
from pcapi.models import db


logger = logging.getLogger(__name__)
blueprint = Blueprint("add_permissions_to_staging_specific_roles", __name__)


def _purge_role_permissions(role: Role) -> None:
    RolePermission.query.filter(RolePermission.roleId == role.id).delete()


@blueprint.cli.command("add_permissions_to_staging_specific_roles")
def add_permissions_to_staging_specific_roles() -> None:
    """Add permissions to qa and global access roles"""

    if settings.IS_PROD:
        logger.error("This function is not supposed to be run on production")
        return

    qa_role = Role.query.filter(Role.name == "qa").one_or_none()
    global_access_role = Role.query.filter(Role.name == "global-access").one_or_none()

    if not qa_role:
        logger.error('"qa" role does not exist.')
        return

    if not global_access_role:
        logger.error('"global-access" role does not exist.')
        return

    # avoid conflicts on RolePermission creations
    _purge_role_permissions(qa_role)
    _purge_role_permissions(global_access_role)

    role_permissions_to_create = []

    for permission in Permission.query.all():
        role_permissions_to_create.append(RolePermission(roleId=qa_role.id, permissionId=permission.id))
        if permission.name != Permissions.MANAGE_PERMISSIONS.name:
            role_permissions_to_create.append(RolePermission(roleId=global_access_role.id, permissionId=permission.id))

    db.session.bulk_save_objects(role_permissions_to_create)
    db.session.commit()

    logger.info("Created permissions for QA and Global Access roles.")
