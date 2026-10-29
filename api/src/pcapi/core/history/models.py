import typing

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext import mutable as sa_mutable

from pcapi.core.chronicles import models as chronicles_models
from pcapi.core.history import constants as history_constants
from pcapi.core.users import models as users_models
from pcapi.models import Model
from pcapi.models.pc_object import PcObject
from pcapi.utils import date as date_utils
from pcapi.utils import db as db_utils


if typing.TYPE_CHECKING:
    from pcapi.core.finance import models as finance_models
    from pcapi.core.offerers import models as offerers_models
    from pcapi.core.offers import models as offers_models


class ActionHistory(PcObject, Model):
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
      stored in a single commit. It would not be possible to store everything in a single db transaction if
      ids were stored as values in a JSONB column.

    Additional information related to a specific action (e.g. reasonCode which is related to user suspension) may be
    stored in extraData field.
    """

    __tablename__ = "action_history"

    actionType: sa_orm.Mapped[history_constants.ActionType] = sa_orm.mapped_column(
        db_utils.MagicEnum(history_constants.ActionType, use_values=True), nullable=False
    )

    # nullable because of old suspensions without date migrated here; but mandatory for new actions
    actionDate = sa_orm.mapped_column(
        sa.DateTime, nullable=True, server_default=sa.func.now(), default=date_utils.get_naive_utc_now
    )

    # User (beneficiary, pro, admin...) who *initiated* the action
    # nullable because of old actions without known author migrated here or lines which must be kept in case an admin
    # author is removed; but the author is mandatory for any new action
    authorUserId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    authorUser: sa_orm.Mapped[users_models.User | None] = sa_orm.relationship("User", foreign_keys=[authorUserId])

    extraData: sa_orm.Mapped[dict | None] = sa_orm.mapped_column(
        "jsonData", sa_mutable.MutableDict.as_mutable(postgresql.JSONB)
    )
    comment: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text(), nullable=True)

    # ActionHistory.userId.is_(None) is used in a query, keep non-conditional index
    userId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=True
    )
    user: sa_orm.Mapped[users_models.User | None] = sa_orm.relationship(
        "User", foreign_keys=[userId], back_populates="action_history"
    )

    # ActionHistory.offererId.is_(None) is used in a query, keep non-conditional index
    offererId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="CASCADE"), index=True, nullable=True
    )
    offerer: sa_orm.Mapped["offerers_models.Offerer | None"] = sa_orm.relationship(
        "Offerer", foreign_keys=[offererId], back_populates="action_history"
    )

    venueId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), nullable=True
    )
    venue: sa_orm.Mapped["offerers_models.Venue | None"] = sa_orm.relationship(
        "Venue", foreign_keys=[venueId], back_populates="action_history"
    )

    financeIncidentId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("finance_incident.id", ondelete="CASCADE"), nullable=True
    )
    financeIncident: sa_orm.Mapped["finance_models.FinanceIncident | None"] = sa_orm.relationship(
        "FinanceIncident",
        foreign_keys=[financeIncidentId],
        back_populates="action_history",
    )

    bankAccountId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("bank_account.id", ondelete="CASCADE"), nullable=True
    )

    bankAccount: sa_orm.Mapped["finance_models.BankAccount | None"] = sa_orm.relationship(
        "BankAccount",
        foreign_keys=[bankAccountId],
        back_populates="action_history",
    )

    ruleId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer_validation_rule.id", ondelete="CASCADE"), nullable=True
    )

    rule: sa_orm.Mapped["offers_models.OfferValidationRule | None"] = sa_orm.relationship(
        "OfferValidationRule",
        foreign_keys=[ruleId],
        back_populates="action_history",
    )

    chronicleId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("chronicle.id", ondelete="CASCADE"), nullable=True
    )

    chronicle: sa_orm.Mapped[chronicles_models.Chronicle | None] = sa_orm.relationship(
        "Chronicle",
        foreign_keys=[chronicleId],
        back_populates="action_history",
    )

    userProfileRefreshCampaignId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger,
        sa.ForeignKey("user_profile_refresh_campaign.id", ondelete="CASCADE"),
        nullable=True,
    )
    userProfileRefreshCampaign: sa_orm.Mapped[users_models.UserProfileRefreshCampaign | None] = sa_orm.relationship(
        "UserProfileRefreshCampaign",
        foreign_keys=[userProfileRefreshCampaignId],
        back_populates="action_history",
    )

    __table_args__ = (
        sa.CheckConstraint(
            (
                'num_nonnulls("userId", "offererId", "venueId", "financeIncidentId", "bankAccountId", "ruleId", "chronicleId", "userProfileRefreshCampaignId") >= 1 '
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
        sa.Index("ix_action_history_actionType", actionType, postgresql_using="hash"),
        sa.Index(
            "ix_action_history_userProfileRefreshCampaignId",
            userProfileRefreshCampaignId,
            postgresql_where=userProfileRefreshCampaignId.is_not(None),
        ),
    )
