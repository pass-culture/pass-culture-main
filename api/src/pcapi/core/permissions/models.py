import enum
import logging
import typing
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

    SUSPEND_USER = "suspendre un compte utilisateur"
    UNSUSPEND_USER = "réactiver un compte utilisateur"

    SEARCH_PRO_ACCOUNT = "rechercher un acteur culturel"
    READ_PRO_ENTITY = "visualiser une structure, un lieu ou un compte pro"
    MANAGE_PRO_ENTITY = "gérer une structure, un lieu ou un compte pro"
    DELETE_PRO_ENTITY = "supprimer une structure ou un lieu"

    MOVE_SIRET = "support pro avancé : déplacer un SIRET"
    MANAGE_PROVIDERS = "support pro avancé : accéder aux pivots"

    MANAGE_BOOKINGS = "gérer les réservations"
    SEARCH_BOOKINGS = "rechercher les réservations"
    READ_BOOKINGS = "visualiser les réservations"

    SEARCH_OFFERS = "rechercher les offres"
    READ_OFFERS = "visualiser les offres"
    MANAGE_OFFERS = "gérer les offres"

    VALIDATE_OFFERER = "gérer la validation des structures et des rattachements"

    MANAGE_OFFERER_TAG = "gérer les tags structure"
    DELETE_OFFERER_TAG = "supprimer un tag (structure, offre, lieu)"

    MANAGE_OFFERS_AND_VENUES_TAGS = "Gérer les tags offres et lieux"

    @classmethod
    def exists(cls, name: str) -> bool:
        try:
            cls[name]
        except KeyError:
            return False
        return True


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


class RolePermission(PcObject, Base, Model):
    """
    An association table between roles and permission for their
    many-to-many relationship
    """

    roleId: int = sa.Column(sa.BigInteger, sa.ForeignKey("role.id", ondelete="CASCADE"))
    permissionId: int = sa.Column(sa.BigInteger, sa.ForeignKey("permission.id", ondelete="CASCADE"))


class Permission(PcObject, Base, Model):
    __tablename__ = "permission"

    name: str = sa.Column(sa.String(length=140), nullable=False, unique=True)
    category = sa.Column(sa.String(140), nullable=True, default=None)
    roles = sa.orm.relationship(  # type: ignore [misc]
        "Role", secondary="role_permission", back_populates="permissions"
    )


class Roles(enum.Enum):
    """
    This enum is synced with the permission table in DB, thanks to the
    sync_enum_with_db_field function which is called when the app is deployed
    """

    ADMIN = "admin"
    SUPPORT_N1 = "support-N1"
    SUPPORT_N2 = "support-N2"
    SUPPORT_PRO = "support-PRO"
    SUPPORT_PRO_N2 = "support-PRO-N2"
    FRAUDE_CONFORMITE = "fraude-conformite"
    DAF = "daf"
    BIZDEV = "bizdev"
    PROGRAMMATION = "programmation"
    PRODUCT_MANAGEMENT = "product-management"
    CHARGE_DEVELOPPEMENT = "charge-developpement"
    HOMOLOGATION = "homologation"


role_backoffice_profile_table = sa.Table(
    "role_backoffice_profile",
    Base.metadata,
    sa.Column("roleId", sa.ForeignKey("role.id", ondelete="CASCADE"), nullable=False, primary_key=True),
    sa.Column(
        "profileId", sa.ForeignKey("backoffice_user_profile.id", ondelete="CASCADE"), nullable=False, primary_key=True
    ),
)


class Role(PcObject, Base, Model):
    __tablename__ = "role"

    name: str = sa.Column(sa.String(140), nullable=False, unique=True)
    permissions = sa.orm.relationship(  # type: ignore [misc]
        Permission, secondary="role_permission", back_populates="roles"
    )
    profiles = sa.orm.relationship("BackOfficeUserProfile", secondary=role_backoffice_profile_table, back_populates="roles")  # type: ignore

    def has_permission(self, needed_permission: Permissions) -> bool:
        for permission in self.permissions:
            if permission.name == needed_permission.name:
                return True
        return False


class BackOfficeUserProfile(Base, Model):
    __tablename__ = "backoffice_user_profile"

    id: int = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    userId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False, unique=True
    )
    user = sa.orm.relationship("User", foreign_keys=[userId], uselist=False, back_populates="backoffice_profile")  # type: ignore
    roles = sa.orm.relationship("Role", secondary=role_backoffice_profile_table, back_populates="profiles")  # type: ignore

    @property
    def permissions(self) -> typing.Collection[Permissions]:
        return [Permissions[perm.name] for role in self.roles for perm in role.permissions]
