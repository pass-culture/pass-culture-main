import enum
import logging
import typing
from typing import TYPE_CHECKING

import flask_sqlalchemy
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql
import sqlalchemy.ext.mutable
import sqlalchemy.orm as sa_orm

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

    READ_PERMISSIONS = "visualiser la matrice des droits"
    MANAGE_PERMISSIONS = "gérer les droits"
    READ_ADMIN_ACCOUNTS = "visualiser les comptes admin"
    MANAGE_ADMIN_ACCOUNTS = "gérer les comptes admin"
    FEATURE_FLIPPING = "activer/désactiver les feature flags"

    PRO_FRAUD_ACTIONS = "actions exclusives à l'équipe Fraude et Conformité (PRO)"
    BENEFICIARY_FRAUD_ACTIONS = "actions exclusives à l'équipe Fraude (jeune)"
    BENEFICIARY_MANUAL_REVIEW = "effectuer une revue manuelle d'obtention de crédit"
    MANAGE_FRAUDULENT_BOOKING_INFO = "marquer les réservations comme frauduleuses ou non frauduleuses"
    READ_FRAUDULENT_BOOKING_INFO = "visualiser les informations sur les réservations frauduleuses"
    READ_BENEFICIARY_BONUS_CREDIT = "visualiser les détails des demandes de bonification"
    REQUEST_BENEFICIARY_BONUS_CREDIT = "demander la bonification pour un bénéficiaire"

    READ_PUBLIC_ACCOUNT = "visualiser un compte bénéficiaire/grand public"
    MANAGE_PUBLIC_ACCOUNT = "gérer un compte bénéficiaire/grand public"
    ANONYMIZE_PUBLIC_ACCOUNT = "anonymiser un compte grand public"
    READ_CHRONICLE = "visualiser les chroniques"
    MANAGE_CHRONICLE = "gérer les chroniques"
    READ_HIGHLIGHT = "visualiser valorisations thématiques"
    MANAGE_HIGHLIGHT = "gérer les valorisations thématiques"
    READ_USER_PROFILE_REFRESH_CAMPAIGN = (
        "visualiser les campagnes de mise à jour des profils bénéficiaires/grand public"
    )
    MANAGE_USER_PROFILE_REFRESH_CAMPAIGN = "gérer les campagnes de mise à jour des profils bénéficiaires/grand public"

    SUSPEND_USER = "suspendre un compte jeune"
    UNSUSPEND_USER = "réactiver un compte jeune"

    READ_PRO_ENTITY = "visualiser une entité juridique, un partenaire culturel ou un compte pro"
    MANAGE_PRO_ENTITY = "gérer une entité juridique, un partenaire culturel ou un compte pro"
    DELETE_PRO_ENTITY = "supprimer une entité juridique ou un partenaire culturel"
    CREATE_PRO_ENTITY = "ajouter un partenaire culturel sans SIRET"
    READ_PRO_ENTREPRISE_INFO = "visualiser les données INSEE/RCS d'une entité juridique"
    READ_PRO_SENSITIVE_INFO = "vérifier les attestations URSSAF/DGFIP d'une entité juridique"
    READ_PRO_AE_INFO = "consulter le suivi de l'inscription d'un Auto-Entrepreneur"
    CONNECT_AS_PRO = "se connecter sur PC Pro en tant qu'AC (connect-as)"

    MOVE_SIRET = "support pro avancé : déplacer ou supprimer un SIRET"
    ADVANCED_PRO_SUPPORT = "support pro avancé"

    MANAGE_BOOKINGS = "gérer les réservations"
    READ_BOOKINGS = "visualiser les réservations"

    READ_OFFERS = "visualiser les offres"
    MANAGE_OFFERS = "gérer les offres"
    MULTIPLE_OFFERS_ACTIONS = "opérations sur plusieurs offres"

    VALIDATE_OFFERER = "gérer la validation des entités juridiques et des rattachements"
    CLOSE_OFFERER = "fermer une entité juridique"

    READ_TAGS = "visualiser les tags entités juridiques, offres, partenaires culturels et jeunes"
    MANAGE_OFFERER_TAG = "gérer les tags entité juridique"
    MANAGE_TAGS_N2 = "supprimer un tag (entité juridique, offre, partenaire culturel) et créer des catégories"
    MANAGE_OFFERS_AND_VENUES_TAGS = "gérer les tags offres et partenaires culturels"

    READ_NON_PAYMENT_NOTICES = "visualiser les avis d'impayés"
    MANAGE_NON_PAYMENT_NOTICES = "gérer les avis d'impayés"

    READ_REIMBURSEMENT_RULES = "visualiser les tarifs dérogatoires"
    CREATE_REIMBURSEMENT_RULES = "créer un tarif dérogatoire"

    CREATE_INCIDENTS = "créer des incidents et gestes commerciaux"
    READ_INCIDENTS = "visualiser les incidents"
    MANAGE_INCIDENTS = "gérer les incidents"
    VALIDATE_COMMERCIAL_GESTURE = "valider les gestes commerciaux"

    READ_TECH_PARTNERS = "visualiser les partenaires techniques"
    MANAGE_TECH_PARTNERS = "gérer les partenaires techniques"

    EXTRACT_PUBLIC_ACCOUNT = "extraire les données personnelles (RGPD) d'un compte"

    READ_SPECIAL_EVENTS = "visualiser les opérations spéciales"
    MANAGE_SPECIAL_EVENTS = "gérer les opérations spéciales"

    MANAGE_ACCOUNT_UPDATE_REQUEST = "instruire les demandes de modification de compte (DS)"
    MANAGE_ACCOUNT_TAGS = "gérer les tags jeunes"
    MANAGE_ACCOUNT_TAGS_N2 = "supprimer un tag jeune et créer des catégories"

    @classmethod
    def exists(cls, name: str) -> bool:
        try:
            cls[name]
        except KeyError:
            return False
        return True


def sync_enum_with_db_field(
    session: sa_orm.scoped_session[flask_sqlalchemy.session.Session],
    py_enum: type[enum.Enum],
    py_attr: str,
    db_class: type[Model],
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


def sync_db_permissions(session: sa_orm.scoped_session[flask_sqlalchemy.session.Session]) -> None:
    """
    Automatically synchronize `permission` table in database from the
    `Permissions` Python Enum.

    This is done before each deployment and in tests
    """
    return sync_enum_with_db_field(session, Permissions, "name", Permission)


class RolePermission(PcObject, Model):
    """
    An association table between roles and permission for their
    many-to-many relationship
    """

    __tablename__ = "role_permission"
    roleId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("role.id", ondelete="CASCADE"), nullable=False
    )
    permissionId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("permission.id", ondelete="CASCADE"), nullable=False
    )
    __table_args__ = (sa.UniqueConstraint("roleId", "permissionId", name="role_permission_roleId_permissionId_key"),)


class Permission(PcObject, Model):
    __tablename__ = "permission"

    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(length=140), nullable=False, unique=True)
    roles: sa_orm.Mapped[list["Role"]] = sa_orm.relationship(
        "Role", secondary=RolePermission.__table__, back_populates="permissions"
    )


class Roles(enum.Enum):
    """
    This enum is synced with the permission table in DB, thanks to the
    sync_enum_with_db_field function which is called when the app is deployed
    """

    ADMIN = "admin"
    CHARGE_DEVELOPPEMENT = "charge_developpement"
    CODIR_ADMIN = "codir_admin"
    COMMUNICATION = "communication"
    CONNECT_AS_PRO = "connect_as_pro"
    DAF = "daf"
    DAF_MANAGEMENT = "responsable_daf"
    DPO = "dpo"
    FRAUDE_CONFORMITE = "fraude_conformite"
    FRAUDE_JEUNES = "fraude_jeunes"
    GLOBAL_ACCESS = "global_access"
    HOMOLOGATION = "homologation"
    HOMOLOGATION_PRO = "homologation_pro"
    LECTURE_SEULE = "lecture_seule"
    PARTENAIRE_TECHNIQUE = "partenaire_technique"
    PERMISSION_MANAGER = "gestionnaire_des_droits"
    PRODUCT_MANAGEMENT = "product_management"
    PROGRAMMATION_MARKET = "programmation_market"
    QA = "qa"
    SUPPORT_N1 = "support_n1"
    SUPPORT_N2 = "support_n2"
    SUPPORT_N3 = "support_n3"
    SUPPORT_PRO = "support_pro"
    SUPPORT_PRO_N2 = "support_pro_n2"
    SUPPORT_PARTENAIRES_TECHNIQUES = "support_partenaires_techniques"


def sync_db_roles(session: sa_orm.scoped_session[flask_sqlalchemy.session.Session]) -> None:
    """
    Automatically synchronize `role` table in database from the
    `Roles` Python Enum.

    This is done before each deployment and in tests
    """
    return sync_enum_with_db_field(session, Roles, "value", Role)


class Role(PcObject, Model):
    __tablename__ = "role"

    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(140), nullable=False, unique=True)
    permissions: sa_orm.Mapped[list["Permission"]] = sa_orm.relationship(
        "Permission", secondary=RolePermission.__table__, back_populates="roles"
    )
    profiles: sa_orm.Mapped[list["BackOfficeUserProfile"]] = sa_orm.relationship(
        "BackOfficeUserProfile", secondary="role_backoffice_profile", back_populates="roles"
    )

    def has_permission(self, needed_permission: Permissions) -> bool:
        for permission in self.permissions:
            if permission.name == needed_permission.name:
                return True
        return False


class BackOfficeUserProfile(Model):
    __tablename__ = "backoffice_user_profile"

    id: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.BigInteger, primary_key=True, autoincrement=True)

    userId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False, unique=True
    )
    user: sa_orm.Mapped["User"] = sa_orm.relationship(
        "User", foreign_keys=[userId], uselist=False, back_populates="backoffice_profile"
    )
    roles: sa_orm.Mapped[list[Role]] = sa_orm.relationship(
        "Role", secondary="role_backoffice_profile", back_populates="profiles"
    )

    preferences: sa_orm.Mapped[dict] = sa_orm.mapped_column(
        sa.ext.mutable.MutableDict.as_mutable(sa.dialects.postgresql.JSONB),
        nullable=False,
        default={},
        server_default="{}",
    )

    # instructor id on Démarche Numérique, used to change application status
    dsInstructorId: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=True, index=True, unique=True)

    @property
    def permissions(self) -> typing.Collection[Permissions]:
        permissions_members = Permissions.__members__
        return [
            Permissions[perm.name]
            for role in self.roles
            for perm in role.permissions
            if perm.name in permissions_members
        ]


RoleBackofficeProfile = sa.Table(
    "role_backoffice_profile",
    Model.metadata,
    sa.Column("roleId", sa.ForeignKey(Role.id, ondelete="CASCADE"), nullable=False, primary_key=True),
    sa.Column(
        "profileId", sa.ForeignKey(BackOfficeUserProfile.id, ondelete="CASCADE"), nullable=False, primary_key=True
    ),
)
