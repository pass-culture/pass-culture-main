"""
Add OpeningHours table
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from pcapi.core.offerers.models import Weekday
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d787e69663b1"
down_revision = "381fef70eb7a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "opening_hours",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("venueId", sa.BigInteger(), nullable=False),
        sa.Column("weekday", MagicEnum(Weekday), nullable=False, default=Weekday.MONDAY),
        sa.Column("timespan", postgresql.ARRAY(postgresql.NUMRANGE()), nullable=True),
        sa.CheckConstraint("cardinality(timespan) <= 2", name="max_timespan_is_2"),
        sa.ForeignKeyConstraint(["venueId"], ["venue.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_opening_hours_venueId"), "opening_hours", ["venueId"], unique=False)


def downgrade() -> None:
    op.drop_table("opening_hours")
