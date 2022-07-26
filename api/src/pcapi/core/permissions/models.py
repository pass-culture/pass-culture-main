import enum
import logging
from typing import Type

import sqlalchemy as sa

from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


logger = logging.getLogger(__name__)


class Permissions(enum.Enum):
    """
    This enum is synced with the permission table in DB, thanks to the
    sync_enum_with_db_field function which is called when the app is deployed
    """

    MANAGE_PERMISSIONS = "gérer les droits"
    SEARCH_PUBLIC_ACCOUNT = "rechercher un compte bénéficiaire/grand public"
    READ_PUBLIC_ACCOUNT = "visualiser un compte bénéficiaire/grand public"
    REVIEW_PUBLIC_ACCOUNT = "faire une revue manuelle d'un compte bénéficiaire/grand public"
    MANAGE_PUBLIC_ACCOUNT = "gérer un compte bénéficiaire/grand public"


def sync_enum_with_db_field(session: sa.orm.Session, py_enum: Type[enum.Enum], db_field: sa.Column) -> None:
    db_values = set(p.name for p in session.query(db_field).all())
    py_values = set(e.name for e in py_enum)

    if removed_permissions := db_values - py_values:
        logger.warning(
            "Some permissions have been removed from code: %s\n"
            "Please check that those permissions are not assigned to any role.",
            ", ".join(removed_permissions),
        )

    if added_permissions := py_values - db_values:
        for perm_name in added_permissions:
            session.add(Permission(name=perm_name))
        session.commit()
        logger.info(
            "%s permission(s) added: %s",
            len(added_permissions),
            ", ".join(added_permissions),
        )


def sync_db_permissions(session: sa.orm.Session) -> None:
    """
    Automatically synchronize `permission` table in database from the
    `Permissions` Python Enum.

    This is done before each deployment and in tests
    """
    return sync_enum_with_db_field(session, Permissions, Permission.name)


role_permission_table = sa.Table(
    "role_permission",
    Base.metadata,
    sa.Column("roleId", sa.ForeignKey("role.id")),
    sa.Column("permissionId", sa.ForeignKey("permission.id")),
    sa.UniqueConstraint("roleId", "permissionId"),
)


class Permission(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    __tablename__ = "permission"

    name = sa.Column(sa.String(length=140), nullable=False, unique=True)
    category = sa.Column(sa.String(140), nullable=True, default=None)
    roles = sa.orm.relationship(  # type: ignore [misc]
        "Role", secondary=role_permission_table, back_populates="permissions"
    )


class Role(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    __tablename__ = "role"

    name = sa.Column(sa.String(140), nullable=False, unique=True)
    permissions = sa.orm.relationship(  # type: ignore [misc]
        Permission, secondary=role_permission_table, back_populates="roles"
    )
