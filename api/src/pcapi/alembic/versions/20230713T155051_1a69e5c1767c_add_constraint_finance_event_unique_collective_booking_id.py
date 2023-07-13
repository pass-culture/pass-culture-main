"""Add partially unique constraint on `finance_event.collectiveBookingId`
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1a69e5c1767c"
down_revision = "0e4772521eb1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "idx_uniq_collective_booking_id",
        "finance_event",
        ["collectiveBookingId"],
        unique=True,
        postgresql_where=sa.text("status IN ('pending', 'ready')"),
    )


def downgrade() -> None:
    op.drop_index(
        "idx_uniq_collective_booking_id",
        table_name="finance_event",
        postgresql_where=sa.text("status IN ('pending', 'ready')"),
    )
