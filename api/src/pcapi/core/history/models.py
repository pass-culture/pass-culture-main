import datetime
import enum
import typing

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext import mutable as sa_mutable
import sqlalchemy.orm as sa_orm

from pcapi.core.chronicles import models as chronicles_models
from pcapi.core.users import models as users_models
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject
from pcapi.utils import db as db_utils


if typing.TYPE_CHECKING:
    from pcapi.core.finance import models as finance_models
    from pcapi.core.offerers import models as offerers_models
    from pcapi.core.offers import models as offers_models


class ActionType(enum.Enum):
    # Single comment from admin, on any resource, without status change:
    COMMENT = "COMMENT"
    # Update:
    INFO_MODIFIED = "INFO_MODIFIED"
    # Validation process for offerers:
    OFFERER_NEW = "OFFERER_NEW"
    OFFERER_PENDING = "OFFERER_PENDING"
    OFFERER_VALIDATED = "OFFERER_VALIDATED"
    OFFERER_REJECTED = "OFFERER_REJECTED"
    OFFERER_CLOSED = "OFFERER_CLOSED"
    OFFERER_SUSPENDED = "OFFERER_SUSPENDED"
    OFFERER_UNSUSPENDED = "OFFERER_UNSUSPENDED"
    OFFERER_ATTESTATION_CHECKED = "OFFERER_ATTESTATION_CHECKED"
    # Validation process for user-offerer relationships:
    USER_OFFERER_NEW = "USER_OFFERER_NEW"
    USER_OFFERER_PENDING = "USER_OFFERER_PENDING"
    USER_OFFERER_VALIDATED = "USER_OFFERER_VALIDATED"
    USER_OFFERER_REJECTED = "USER_OFFERER_REJECTED"
    USER_OFFERER_DELETED = "USER_OFFERER_DELETED"
    # User account status changes:
    USER_CREATED = "USER_CREATED"
    USER_SUSPENDED = "USER_SUSPENDED"
    USER_UNSUSPENDED = "USER_UNSUSPENDED"
    USER_PHONE_VALIDATED = "USER_PHONE_VALIDATED"
    USER_EMAIL_VALIDATED = "USER_EMAIL_VALIDATED"
    USER_ACCOUNT_UPDATE_INSTRUCTED = "USER_ACCOUNT_UPDATE_INSTRUCTED"
    USER_EXTRACT_DATA = "USER_EXTRACT_DATA"
    CONNECT_AS_USER = "CONNECT_AS_USER"
    USER_PASSWORD_INVALIDATED = "USER_PASSWORD_INVALIDATED"
    # Fraud and compliance actions:
    BLACKLIST_DOMAIN_NAME = "BLACKLIST_DOMAIN_NAME"
    REMOVE_BLACKLISTED_DOMAIN_NAME = "REMOVE_BLACKLISTED_DOMAIN_NAME"
    FRAUD_INFO_MODIFIED = "FRAUD_INFO_MODIFIED"  # protected information

    # Finance incident events
    FINANCE_INCIDENT_CREATED = "FINANCE_INCIDENT_CREATED"
    FINANCE_INCIDENT_CANCELLED = "FINANCE_INCIDENT_CANCELLED"
    FINANCE_INCIDENT_VALIDATED = "FINANCE_INCIDENT_VALIDATED"
    FINANCE_INCIDENT_USER_RECREDIT = "FINANCE_INCIDENT_USER_RECREDIT"
    FINANCE_INCIDENT_WAIT_FOR_PAYMENT = "FINANCE_INCIDENT_WAIT_FOR_PAYMENT"
    FINANCE_INCIDENT_GENERATE_DEBIT_NOTE = "FINANCE_INCIDENT_GENERATE_DEBIT_NOTE"
    FINANCE_INCIDENT_CHOOSE_DEBIT_NOTE = "FINANCE_INCIDENT_CHOOSE_DEBIT_NOTE"

    # Actions related to a venue:
    VENUE_CREATED = "VENUE_CREATED"
    LINK_VENUE_BANK_ACCOUNT_DEPRECATED = "LINK_VENUE_BANK_ACCOUNT_DEPRECATED"
    LINK_VENUE_BANK_ACCOUNT_CREATED = "LINK_VENUE_BANK_ACCOUNT_CREATED"
    LINK_VENUE_PROVIDER_UPDATED = "LINK_VENUE_PROVIDER_UPDATED"
    LINK_VENUE_PROVIDER_DELETED = "LINK_VENUE_PROVIDER_DELETED"
    SYNC_VENUE_TO_PROVIDER = "SYNC_VENUE_TO_PROVIDER"

    # Permissions role changes:
    ROLE_PERMISSIONS_CHANGED = "ROLE_PERMISSIONS_CHANGED"
    # RGPD scripts
    USER_ANONYMIZED = "USER_ANONYMIZED"
    # Offer validation rule changes:
    RULE_CREATED = "RULE_CREATED"
    RULE_DELETED = "RULE_DELETED"
    RULE_MODIFIED = "RULE_MODIFIED"
    # Pivot changes
    PIVOT_DELETED = "PIVOT_DELETED"
    PIVOT_CREATED = "PIVOT_CREATED"
    # Chronicles
    CHRONICLE_PUBLISHED = "CHRONICLE_PUBLISHED"
    CHRONICLE_UNPUBLISHED = "CHRONICLE_UNPUBLISHED"


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

    actionType: ActionType = sa.Column(db_utils.MagicEnum(ActionType), nullable=False)
    sa.Index("ix_action_history_actionType", actionType, postgresql_using="hash")

    # nullable because of old suspensions without date migrated here; but mandatory for new actions
    actionDate = sa.Column(sa.DateTime, nullable=True, server_default=sa.func.now(), default=datetime.datetime.utcnow)

    # User (beneficiary, pro, admin...) who *initiated* the action
    # nullable because of old actions without known author migrated here or lines which must be kept in case an admin
    # author is removed; but the author is mandatory for any new action
    authorUserId: int | None = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    authorUser: sa_orm.Mapped[users_models.User | None] = sa_orm.relationship("User", foreign_keys=[authorUserId])

    extraData: sa_orm.Mapped[dict | None] = sa.Column("jsonData", sa_mutable.MutableDict.as_mutable(postgresql.JSONB))

    # ActionHistory.userId.is_(None) is used in a query, keep non-conditional index
    userId: int | None = sa.Column(
        sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=True
    )
    user: sa_orm.Mapped[users_models.User | None] = sa_orm.relationship(
        "User",
        foreign_keys=[userId],
        backref=sa_orm.backref("action_history", order_by=ACTION_HISTORY_ORDER_BY, passive_deletes=True),
    )

    # ActionHistory.offererId.is_(None) is used in a query, keep non-conditional index
    offererId: int | None = sa.Column(
        sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="CASCADE"), index=True, nullable=True
    )
    offerer: sa_orm.Mapped["offerers_models.Offerer | None"] = sa_orm.relationship(
        "Offerer",
        foreign_keys=[offererId],
        backref=sa_orm.backref("action_history", order_by=ACTION_HISTORY_ORDER_BY, passive_deletes=True),
    )

    venueId: int | None = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), nullable=True)
    venue: sa_orm.Mapped["offerers_models.Venue | None"] = sa_orm.relationship(
        "Venue",
        foreign_keys=[venueId],
        backref=sa_orm.backref("action_history", order_by=ACTION_HISTORY_ORDER_BY, passive_deletes=True),
    )

    financeIncidentId: int | None = sa.Column(
        sa.BigInteger, sa.ForeignKey("finance_incident.id", ondelete="CASCADE"), nullable=True
    )
    financeIncident: sa_orm.Mapped["finance_models.FinanceIncident | None"] = sa_orm.relationship(
        "FinanceIncident",
        foreign_keys=[financeIncidentId],
        backref=sa_orm.backref("action_history", order_by="ActionHistory.actionDate.asc()", passive_deletes=True),
    )

    bankAccountId: int | None = sa.Column(
        sa.BigInteger, sa.ForeignKey("bank_account.id", ondelete="CASCADE"), nullable=True
    )

    bankAccount: sa_orm.Mapped["finance_models.BankAccount | None"] = sa_orm.relationship(
        "BankAccount",
        foreign_keys=[bankAccountId],
        backref=sa_orm.backref("action_history", order_by=ACTION_HISTORY_ORDER_BY, passive_deletes=True),
    )

    ruleId: int | None = sa.Column(
        sa.BigInteger, sa.ForeignKey("offer_validation_rule.id", ondelete="CASCADE"), nullable=True
    )

    rule: sa_orm.Mapped["offers_models.OfferValidationRule | None"] = sa_orm.relationship(
        "OfferValidationRule",
        foreign_keys=[ruleId],
        backref=sa_orm.backref("action_history", order_by=ACTION_HISTORY_ORDER_BY, passive_deletes=True),
    )

    chronicleId: int | None = sa.Column(sa.BigInteger, sa.ForeignKey("chronicle.id", ondelete="CASCADE"), nullable=True)

    chronicle: sa_orm.Mapped[chronicles_models.Chronicle | None] = sa_orm.relationship(
        "Chronicle",
        foreign_keys=[chronicleId],
        backref=sa_orm.backref("action_history", order_by=ACTION_HISTORY_ORDER_BY, passive_deletes=True),
    )

    comment = sa.Column(sa.Text(), nullable=True)

    __table_args__ = (
        sa.CheckConstraint(
            (
                'num_nonnulls("userId", "offererId", "venueId", "financeIncidentId", "bankAccountId", "ruleId", "chronicleId") >= 1 '
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
        sa.Index("ix_action_history_chronicleId", chronicleId, postgresql_where=chronicleId.is_not(None)),
    )
