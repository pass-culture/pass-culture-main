"""Change highlight timespan to datespan step 1 of 2
Change column type from tsrang to daterange"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b1b0355dabed"
down_revision = "3c967a1782c0"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute(
        sa.text(
            """ALTER TABLE highlight ALTER COLUMN availability_timespan type daterange USING daterange(lower(availability_timespan)::date, upper(availability_timespan)::date);"""
        )
    )
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute(
        sa.text(
            """ALTER TABLE highlight ALTER COLUMN highlight_timespan type daterange USING daterange(lower(highlight_timespan)::date, upper(highlight_timespan)::date);"""
        )
    )


def downgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute(
        sa.text(
            """ALTER TABLE highlight ALTER COLUMN availability_timespan type tsrange USING tsrange(lower(availability_timespan)::date, upper(availability_timespan)::date);"""
        )
    )
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute(
        sa.text(
            """ALTER TABLE highlight ALTER COLUMN highlight_timespan type tsrange USING tsrange(lower(highlight_timespan)::date, upper(highlight_timespan)::date);"""
        )
    )
