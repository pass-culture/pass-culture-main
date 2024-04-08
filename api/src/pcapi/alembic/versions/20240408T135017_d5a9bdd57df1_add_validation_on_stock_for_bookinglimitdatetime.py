"""
add validation on stock for bookingLimitDatetime
"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d5a9bdd57df1"
down_revision = "374e35815645"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute(
        """
        alter table
            stock
        add
            constraint "check_bookingLimitDatetime_not_too_late" CHECK ("bookingLimitDatetime" < "beginningDatetime");
    """
    )


def downgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute(
        """
        alter table
            stock
        drop
            constraint if exists "check_bookingLimitDatetime_not_too_late" 
    """
    )
