"""Drop event_opening_hours and event_week_day_opening_hours tables"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from pcapi.core.offers.models import Weekday
from pcapi.utils.db import MagicEnum


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3f4006677b43"
down_revision = "1d148db32d66"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_table("event_week_day_opening_hours")
    op.drop_table("event_opening_hours")


def downgrade() -> None:
    op.create_table(
        "event_opening_hours",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("isSoftDeleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("offerId", sa.BigInteger(), nullable=False),
        sa.Column("dateCreated", sa.DateTime(), nullable=False),
        sa.Column("dateUpdated", sa.DateTime(), nullable=True),
        sa.Column("startDatetime", sa.DateTime(), nullable=False),
        sa.Column("endDatetime", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["offerId"],
            ["offer.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_event_opening_hours_offerId"), "event_opening_hours", ["offerId"], unique=False)
    op.create_table(
        "event_week_day_opening_hours",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("eventOpeningHoursId", sa.BigInteger(), nullable=False),
        sa.Column("weekday", MagicEnum(Weekday), nullable=False),
        sa.Column("timeSpans", postgresql.ARRAY(postgresql.NUMRANGE())),
        sa.CheckConstraint('cardinality("timeSpans") <= 2', name="max_timespan_is_2"),
        sa.ForeignKeyConstraint(["eventOpeningHoursId"], ["event_opening_hours.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("weekday", "eventOpeningHoursId", name="unique_weekday_eventOpeningHoursDetailsId"),
    )
    op.create_index(
        op.f("ix_event_week_day_opening_hours_eventOpeningHoursId"),
        "event_week_day_opening_hours",
        ["eventOpeningHoursId"],
        unique=False,
    )
