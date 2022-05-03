"""add unique constraint to allocine_pivot
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "ab3a9d7b221b"
down_revision = "04bebeb57442"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE allocine_pivot ADD CONSTRAINT "allocine_pivot_venueId_key" UNIQUE USING INDEX "ix_allocine_pivot_venueId"
        """
    )


def downgrade() -> None:
    op.drop_constraint("allocine_pivot_venueId_key", table_name="allocine_pivot")
