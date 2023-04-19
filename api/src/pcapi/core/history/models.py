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
    from pcapi.core.offerers import models as offerers_models


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
    # Validation process for user-offerer relationships:
    USER_OFFERER_NEW = "Nouveau rattachement"
    USER_OFFERER_PENDING = "Rattachement mis en attente"
    USER_OFFERER_VALIDATED = "Rattachement validé"
    USER_OFFERER_REJECTED = "Rattachement rejeté"
    # User account status changes:
    USER_CREATED = "Création du compte"
    USER_SUSPENDED = "Compte suspendu"
    USER_UNSUSPENDED = "Compte réactivé"
    USER_PHONE_VALIDATED = "Validation manuelle du numéro de téléphone"
    USER_EMAIL_VALIDATED = "Validation manuelle de l'e-mail"


class ActionHistory(PcObject, Base, Model):
    """
    This table aims at logging all actions that should appear in a resource history for support, fraud team, etc.

    user, offerer, venue are filled in the log entry depending on the action. So they are nullable.
    Example: When a user requests to be attached to an offerer, action has both userId and offererId, but no venueId.
    This enables to filter on either the user or the offerer, and the same action appears in both user history and
    offerer history in the backoffice.

    user, offerer and venue ids have a dedicated column in the table because this enables to:
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

    # nullable because of old suspensions without date migrated here; but mandatory for new actions
    actionDate = sa.Column(sa.DateTime, nullable=True, server_default=sa.func.now())

    # User (beneficiary, pro, admin...) who *initiated* the action
    # nullable because of old actions without known author migrated here or lines which must be kept in case an admin
    # author is removed; but the author is mandatory for any new action
    authorUserId: int | None = sa.Column(sa.BigInteger, sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    authorUser: users_models.User | None = sa.orm.relationship("User", foreign_keys=[authorUserId])

    extraData: sa_orm.Mapped[dict | None] = sa.Column("jsonData", sa_mutable.MutableDict.as_mutable(postgresql.JSONB))

    userId: int | None = sa.Column(
        sa.BigInteger, sa.ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=True
    )
    user: users_models.User | None = sa.orm.relationship(
        "User",
        foreign_keys=[userId],
        backref=sa.orm.backref(
            "action_history", order_by="ActionHistory.actionDate.asc().nullsfirst()", passive_deletes=True
        ),
    )

    offererId: int | None = sa.Column(
        sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="CASCADE"), index=True, nullable=True
    )
    offerer: sa.orm.Mapped["offerers_models.Offerer | None"] = sa.orm.relationship(
        "Offerer",
        foreign_keys=[offererId],
        backref=sa.orm.backref(
            "action_history", order_by="ActionHistory.actionDate.asc().nullsfirst()", passive_deletes=True
        ),
    )

    venueId: int | None = sa.Column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), index=True, nullable=True
    )
    venue: sa.orm.Mapped["offerers_models.Venue | None"] = sa.orm.relationship(
        "Venue",
        foreign_keys=[venueId],
        backref=sa.orm.backref(
            "action_history", order_by="ActionHistory.actionDate.asc().nullsfirst()", passive_deletes=True
        ),
    )

    comment = sa.Column(sa.Text(), nullable=True)

    __table_args__ = (
        sa.CheckConstraint('num_nonnulls("userId", "offererId", "venueId") >= 1', name="check_at_least_one_resource"),
    )
