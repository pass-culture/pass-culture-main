import logging

from flask import Blueprint

from pcapi import settings
from pcapi.core.permissions import models as perm_models
from pcapi.models import db


logger = logging.getLogger(__name__)
blueprint = Blueprint("add_permissions_to_staging_specific_roles", __name__)


def _purge_role_permissions(role: perm_models.Role) -> None:
    db.session.query(perm_models.RolePermission).filter(perm_models.RolePermission.roleId == role.id).delete()


@blueprint.cli.command("add_permissions_to_staging_specific_roles")
def add_permissions_to_staging_specific_roles() -> None:
    """Add permissions to qa and global access roles"""

    if not settings.BACKOFFICE_ADD_ALL_PERMISSIONS_TO_SPECIFIC_ROLES:
        logger.error("This function is not supposed to be run on production")
        return

    qa_role = (
        db.session.query(perm_models.Role).filter(perm_models.Role.name == perm_models.Roles.QA.value).one_or_none()
    )
    global_access_role = (
        db.session.query(perm_models.Role)
        .filter(perm_models.Role.name == perm_models.Roles.GLOBAL_ACCESS.value)
        .one_or_none()
    )

    if not qa_role:
        logger.error("'%s' role does not exist.", perm_models.Roles.QA.value)
        return

    if not global_access_role:
        logger.error("'%s' role does not exist.", perm_models.Roles.GLOBAL_ACCESS.value)
        return

    # avoid conflicts on RolePermission creations
    _purge_role_permissions(qa_role)
    _purge_role_permissions(global_access_role)

    role_permissions_to_create = []

    for permission in db.session.query(perm_models.Permission).all():
        role_permissions_to_create.append(perm_models.RolePermission(roleId=qa_role.id, permissionId=permission.id))
        if permission.name != perm_models.Permissions.MANAGE_PERMISSIONS.name:
            role_permissions_to_create.append(
                perm_models.RolePermission(roleId=global_access_role.id, permissionId=permission.id)
            )

    db.session.bulk_save_objects(role_permissions_to_create)
    db.session.commit()

    logger.info("Created permissions for QA and Global Access roles.")
