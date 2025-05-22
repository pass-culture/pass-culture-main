"""Add foreign key constraint on stock.eventOpeningHoursId"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "dc00a380dc2e"
down_revision = "d25a79f51151"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "stock" ADD CONSTRAINT "stock_eventOpeningHoursId_fkey" FOREIGN KEY("eventOpeningHoursId") REFERENCES event_opening_hours (id) NOT VALID;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE "stock" DROP CONSTRAINT IF EXISTS "stock_eventOpeningHoursId_fkey";
        """
    )
