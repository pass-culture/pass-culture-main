import enum
import typing

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext import mutable as sa_mutable
import sqlalchemy.orm as sa_orm

from pcapi.core.users import models as users_models
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


if typing.TYPE_CHECKING:
    from pcapi.core.finance import models as finance_models
    from pcapi.core.offerers import models as offerers_models
    from pcapi.core.offers import models as offers_models


class ActionType(enum.Enum):
    # Single comment from admin, on any resource, without status change:
    COMMENT = "Commentaire interne"
    # Update:
    INFO_MODIFIED = "Modification des informations"
    # Validation process for offerers:
    OFFERER_NEW = "Nouvelle structure"
    OFFERER_PENDING = "Structure mise en attente"
    OFFERER_VALIDATED = "Structure validée"
    OFFERER_REJECTED = "Structure rejetée"
    OFFERER_SUSPENDED = "Structure désactivée"
    OFFERER_UNSUSPENDED = "Structure réactivée"
    OFFERER_ATTESTATION_CHECKED = "Attestation consultée"
    # Validation process for user-offerer relationships:
    USER_OFFERER_NEW = "Nouveau rattachement"
    USER_OFFERER_PENDING = "Rattachement mis en attente"
    USER_OFFERER_VALIDATED = "Rattachement validé"
    USER_OFFERER_REJECTED = "Rattachement rejeté"
    USER_OFFERER_DELETED = "Rattachement supprimé, sans mail envoyé"
    # User account status changes:
    USER_CREATED = "Création du compte"
    USER_SUSPENDED = "Compte suspendu"
    USER_UNSUSPENDED = "Compte réactivé"
    USER_PHONE_VALIDATED = "Validation manuelle du numéro de téléphone"
    USER_EMAIL_VALIDATED = "Validation manuelle de l'email"
    USER_EXTRACT_DATA = "Génération d'un extrait des données du compte"
    CONNECT_AS_USER = "Connexion d'un admin"
    # Fraud and compliance actions:
    BLACKLIST_DOMAIN_NAME = "Blacklist d'un nom de domaine"
    REMOVE_BLACKLISTED_DOMAIN_NAME = "Suppression d'un nom de domaine banni"
    FRAUD_INFO_MODIFIED = "Fraude et Conformité"  # protected information

    # Finance incident events
    FINANCE_INCIDENT_CREATED = "Création de l'incident"
    FINANCE_INCIDENT_CANCELLED = "Annulation de l'incident"
    FINANCE_INCIDENT_VALIDATED = "Validation de l'incident"
    FINANCE_INCIDENT_USER_RECREDIT = "Compte re-crédité suite à un incident"
    FINANCE_INCIDENT_WAIT_FOR_PAYMENT = "Attente de la prochaine échéance de remboursement"
    FINANCE_INCIDENT_GENERATE_DEBIT_NOTE = "Une note de débit va être générée"
    FINANCE_INCIDENT_CHOOSE_DEBIT_NOTE = "Choix note de débit"

    # Actions related to a venue:
    VENUE_CREATED = "Lieu créé"
    LINK_VENUE_BANK_ACCOUNT_DEPRECATED = "Lieu dissocié d'un compte bancaire"
    LINK_VENUE_BANK_ACCOUNT_CREATED = "Lieu associé à un compte bancaire"
    LINK_VENUE_PROVIDER_DELETED = "Suppression du lien avec le provider"

    # Permissions role changes:
    ROLE_PERMISSIONS_CHANGED = "Modification des permissions du rôle"
    # RGPD scripts
    USER_ANONYMIZED = "Le compte a été anonymisé conformément au RGPD"
    # Offer validation rule changes:
    RULE_CREATED = "Création d'une règle de conformité"
    RULE_DELETED = "Suppression d'une règle de conformité"
    RULE_MODIFIED = "Modification d'une règle de conformité"
    # Pivot changes
    PIVOT_DELETED = "Suppression d'un pivot"


ACTION_HISTORY_ORDER_BY = "ActionHistory.actionDate.asc().nulls_first()"


class ActionHistory(PcObject, Base, Model):
    """
    This table aims at logging all actions that should appear in a resource history for support, fraud team, etc.

    user, offerer, venue, bank account are filled in the log entry depending on the action. So they are nullable.
    Example: When a user requests to be attached to an offerer, action has both userId and offererId, but no venueId.
    This enables to filter on either the user or the offerer, and the same action appears in both user history and
    offerer history in the backoffice.

    user, offerer, venue and bank account ids have a dedicated column in the table because this enables to:
    - easily index and filter to get history list for a resource or select items directly in database for debug
      (even if this is also possible with JSONB, but using more complex filter in requests),
    - have a constraint which forces to link the action to at least one resource,
    - join with user, offerer and venue tables to get the resource data without additional requests
    - create an action on a resource which is not stored in database yet, so does not have id, so that all objects are
      stored in a single repository.save(). It would not be possible to store everything in a single db transaction if
      ids were stored as values in a JSONB column.

    Additional information related to a specific action (e.g. reasonCode which is related to user suspension) may be
    stored in extraData field.
    """

    __tablename__ = "action_history"

    actionType: ActionType = sa.Column(sa.Enum(ActionType, create_constraint=False), nullable=False)
    sa.Index("ix_action_history_actionType", actionType, postgresql_using="hash")

    # nullable because of old suspensions without date migrated here; but mandatory for new actions
    actionDate = sa.Column(sa.DateTime, nullable=True, server_default=sa.func.now())

    # User (beneficiary, pro, admin...) who *initiated* the action
    # nullable because of old actions without known author migrated here or lines which must be kept in case an admin
    # author is removed; but the author is mandatory for any new action
    authorUserId: int | None = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    authorUser: users_models.User | None = sa.orm.relationship("User", foreign_keys=[authorUserId])

    extraData: sa_orm.Mapped[dict | None] = sa.Column("jsonData", sa_mutable.MutableDict.as_mutable(postgresql.JSONB))

    # ActionHistory.userId.is_(None) is used in a query, keep non-conditional index
    userId: int | None = sa.Column(
        sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=True
    )
    user: users_models.User | None = sa.orm.relationship(
        "User",
        foreign_keys=[userId],
        backref=sa.orm.backref("action_history", order_by=ACTION_HISTORY_ORDER_BY, passive_deletes=True),
    )

    # ActionHistory.offererId.is_(None) is used in a query, keep non-conditional index
    offererId: int | None = sa.Column(
        sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="CASCADE"), index=True, nullable=True
    )
    offerer: sa.orm.Mapped["offerers_models.Offerer | None"] = sa.orm.relationship(
        "Offerer",
        foreign_keys=[offererId],
        backref=sa.orm.backref("action_history", order_by=ACTION_HISTORY_ORDER_BY, passive_deletes=True),
    )

    venueId: int | None = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), nullable=True)
    venue: sa.orm.Mapped["offerers_models.Venue | None"] = sa.orm.relationship(
        "Venue",
        foreign_keys=[venueId],
        backref=sa.orm.backref("action_history", order_by=ACTION_HISTORY_ORDER_BY, passive_deletes=True),
    )

    financeIncidentId: int | None = sa.Column(
        sa.BigInteger, sa.ForeignKey("finance_incident.id", ondelete="CASCADE"), nullable=True
    )
    financeIncident: sa.orm.Mapped["finance_models.FinanceIncident | None"] = sa.orm.relationship(
        "FinanceIncident",
        foreign_keys=[financeIncidentId],
        backref=sa.orm.backref("action_history", order_by="ActionHistory.actionDate.asc()", passive_deletes=True),
    )

    bankAccountId: int | None = sa.Column(
        sa.BigInteger, sa.ForeignKey("bank_account.id", ondelete="CASCADE"), nullable=True
    )

    bankAccount: sa.orm.Mapped["finance_models.BankAccount | None"] = sa.orm.relationship(
        "BankAccount",
        foreign_keys=[bankAccountId],
        backref=sa.orm.backref("action_history", order_by=ACTION_HISTORY_ORDER_BY, passive_deletes=True),
    )

    ruleId: int | None = sa.Column(
        sa.BigInteger, sa.ForeignKey("offer_validation_rule.id", ondelete="CASCADE"), nullable=True
    )

    rule: sa.orm.Mapped["offers_models.OfferValidationRule | None"] = sa.orm.relationship(
        "OfferValidationRule",
        foreign_keys=[ruleId],
        backref=sa.orm.backref("action_history", order_by=ACTION_HISTORY_ORDER_BY, passive_deletes=True),
    )

    comment = sa.Column(sa.Text(), nullable=True)

    __table_args__ = (
        sa.CheckConstraint(
            (
                'num_nonnulls("userId", "offererId", "venueId", "financeIncidentId", "bankAccountId", "ruleId") >= 1 '
                'OR actionType = "BLACKLIST_DOMAIN_NAME" OR actionType = "REMOVE_BLACKLISTED_DOMAIN_NAME" '
                'OR actionType = "ROLE_PERMISSIONS_CHANGED"'
            ),
            name="check_action_resource",
        ),
        sa.Index("ix_action_history_venueId", venueId, postgresql_where=venueId.is_not(None)),
        sa.Index(
            "ix_action_history_financeIncidentId", financeIncidentId, postgresql_where=financeIncidentId.is_not(None)
        ),
        sa.Index("ix_action_history_bankAccountId", bankAccountId, postgresql_where=bankAccountId.is_not(None)),
        sa.Index("ix_action_history_ruleId", ruleId, postgresql_where=ruleId.is_not(None)),
    )
