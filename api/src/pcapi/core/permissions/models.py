import enum
import logging
import typing
from typing import TYPE_CHECKING

import sqlalchemy as sa

from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from pcapi.core.users.models import User


class Permissions(enum.Enum):
    """
    This enum is synced with the permission table in DB, thanks to the
    sync_enum_with_db_field function which is called when the app is deployed
    """

    MANAGE_PERMISSIONS = "gérer les droits"
    READ_ADMIN_ACCOUNTS = "visualiser les comptes admin"
    MANAGE_ADMIN_ACCOUNTS = "gérer les comptes admin"
    FEATURE_FLIPPING = "activer/désactiver les feature flags"

    PRO_FRAUD_ACTIONS = "actions exclusives à l'équipe Fraude et Conformité (PRO)"
    BENEFICIARY_FRAUD_ACTIONS = "actions exclusives à l'équipe Fraude (jeune)"

    READ_PUBLIC_ACCOUNT = "visualiser un compte bénéficiaire/grand public"
    MANAGE_PUBLIC_ACCOUNT = "gérer un compte bénéficiaire/grand public"
    ANONYMIZE_PUBLIC_ACCOUNT = "Anonymiser un compte grand public"

    SUSPEND_USER = "suspendre un compte jeune"
    UNSUSPEND_USER = "réactiver un compte jeune"

    READ_PRO_ENTITY = "visualiser une structure, un lieu ou un compte pro"
    MANAGE_PRO_ENTITY = "gérer une structure, un lieu ou un compte pro"
    DELETE_PRO_ENTITY = "supprimer une structure ou un lieu"
    CREATE_PRO_ENTITY = "créer une structure"
    READ_PRO_ENTREPRISE_INFO = "visualiser les données INSEE/RCS d'une structure"
    READ_PRO_SENSITIVE_INFO = "vérifier les attestations URSSAF/DGFIP d'une structure"
    READ_PRO_AE_INFO = "consulter le suivi de l'inscription d'un Auto-Entrepreneur"

    MOVE_SIRET = "support pro avancé : déplacer ou supprimer un SIRET"
    ADVANCED_PRO_SUPPORT = "support pro avancé"

    MANAGE_BOOKINGS = "gérer les réservations"
    READ_BOOKINGS = "visualiser les réservations"

    READ_OFFERS = "visualiser les offres"
    MANAGE_OFFERS = "gérer les offres"
    MULTIPLE_OFFERS_ACTIONS = "opérations sur plusieurs offres"

    VALIDATE_OFFERER = "gérer la validation des structures et des rattachements"

    READ_TAGS = "visualiser les tags structure, offres et lieux"
    MANAGE_OFFERER_TAG = "gérer les tags structure"
    MANAGE_TAGS_N2 = "supprimer un tag (structure, offre, lieu) et créer des catégories"
    MANAGE_OFFERS_AND_VENUES_TAGS = "gérer les tags offres et lieux"

    READ_REIMBURSEMENT_RULES = "visualiser les tarifs dérogatoires"
    CREATE_REIMBURSEMENT_RULES = "créer un tarif dérogatoire"

    READ_INCIDENTS = "visualiser les incidents"
    MANAGE_INCIDENTS = "gérer les incidents"
    VALIDATE_COMMERCIAL_GESTURE = "valider les gestes commerciaux"

    GENERATE_INVOICES = "générer les justificatifs de remboursement"

    MANAGE_TECH_PARTNERS = "gérer les partenaires techniques"

    EXTRACT_PUBLIC_ACCOUNT = "extraire les données personnelles (RGPD) d'un compte"

    @classmethod
    def exists(cls, name: str) -> bool:
        try:
            cls[name]
        except KeyError:
            return False
        return True


def sync_enum_with_db_field(
    session: sa.orm.Session, py_enum: type[enum.Enum], py_attr: str, db_class: type[Model]
) -> None:
    db_values = set(p.name for p in session.query(db_class.name).all())
    py_values = set(getattr(e, py_attr) for e in py_enum)

    if removed_names := db_values - py_values:
        logger.warning(
            "Some %ss have been removed from code: %s\nPlease check that those %ss are not assigned to any role.",
            db_class.__name__,
            ", ".join(removed_names),
            db_class.__name__,
        )

    if added_names := py_values - db_values:
        for name in added_names:
            session.add(db_class(name=name))
        session.commit()
        logger.info(
            "%s %s(s) added: %s",
            len(added_names),
            db_class.__name__,
            ", ".join(added_names),
        )


def sync_db_permissions(session: sa.orm.Session) -> None:
    """
    Automatically synchronize `permission` table in database from the
    `Permissions` Python Enum.

    This is done before each deployment and in tests
    """
    return sync_enum_with_db_field(session, Permissions, "name", Permission)


class RolePermission(PcObject, Base, Model):
    """
    An association table between roles and permission for their
    many-to-many relationship
    """

    roleId: int = sa.Column(sa.BigInteger, sa.ForeignKey("role.id", ondelete="CASCADE"))
    permissionId: int = sa.Column(sa.BigInteger, sa.ForeignKey("permission.id", ondelete="CASCADE"))
    __table_args__ = (sa.UniqueConstraint("roleId", "permissionId", name="role_permission_roleId_permissionId_key"),)


class Permission(PcObject, Base, Model):
    __tablename__ = "permission"

    name: str = sa.Column(sa.String(length=140), nullable=False, unique=True)
    category = sa.Column(sa.String(140), nullable=True, default=None)
    roles: sa.orm.Mapped["Role"] = sa.orm.relationship(
        "Role", secondary="role_permission", back_populates="permissions"
    )


class Roles(enum.Enum):
    """
    This enum is synced with the permission table in DB, thanks to the
    sync_enum_with_db_field function which is called when the app is deployed
    """

    ADMIN = "admin"
    CODIR_ADMIN = "codir_admin"
    SUPPORT_N1 = "support_n1"
    SUPPORT_N2 = "support_n2"
    SUPPORT_PRO = "support_pro"
    SUPPORT_PRO_N2 = "support_pro_n2"
    FRAUDE_CONFORMITE = "fraude_conformite"
    FRAUDE_JEUNES = "fraude_jeunes"
    DAF_MANAGEMENT = "responsable_daf"
    DAF = "daf"
    PARTENAIRE_TECHNIQUE = "partenaire_technique"
    PROGRAMMATION_MARKET = "programmation_market"
    PRODUCT_MANAGEMENT = "product_management"
    CHARGE_DEVELOPPEMENT = "charge_developpement"
    HOMOLOGATION = "homologation"
    LECTURE_SEULE = "lecture_seule"
    QA = "qa"
    GLOBAL_ACCESS = "global_access"
    DPO = "dpo"
    PERMISSION_MANAGER = "gestionnaire_des_droits"


def sync_db_roles(session: sa.orm.Session) -> None:
    """
    Automatically synchronize `role` table in database from the
    `Roles` Python Enum.

    This is done before each deployment and in tests
    """
    return sync_enum_with_db_field(session, Roles, "value", Role)


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
    permissions: sa.orm.Mapped["Permission"] = sa.orm.relationship(
        Permission, secondary="role_permission", back_populates="roles"
    )
    profiles: sa.orm.Mapped["BackOfficeUserProfile"] = sa.orm.relationship(
        "BackOfficeUserProfile", secondary=role_backoffice_profile_table, back_populates="roles"
    )

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
    user: sa.orm.Mapped["User"] = sa.orm.relationship(
        "User", foreign_keys=[userId], uselist=False, back_populates="backoffice_profile"
    )
    roles: sa.orm.Mapped["list[Role]"] = sa.orm.relationship(
        "Role", secondary=role_backoffice_profile_table, back_populates="profiles"
    )

    preferences: sa.orm.Mapped[dict] = sa.Column(
        sa.ext.mutable.MutableDict.as_mutable(sa.dialects.postgresql.JSONB),
        nullable=False,
        default={},
        server_default="{}",
    )

    @property
    def permissions(self) -> typing.Collection[Permissions]:
        permissions_members = Permissions.__members__
        return [
            Permissions[perm.name]
            for role in self.roles
            for perm in role.permissions
            if perm.name in permissions_members
        ]
