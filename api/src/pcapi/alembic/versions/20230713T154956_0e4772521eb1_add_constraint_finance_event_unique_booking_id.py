"""Add partially unique constraint on `finance_event.bookingId`
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0e4772521eb1"
down_revision = "d0595349bc22"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "idx_uniq_individual_booking_id",
        "finance_event",
        ["bookingId"],
        unique=True,
        postgresql_where=sa.text("status IN ('pending', 'ready')"),
    )


def downgrade() -> None:
    op.drop_index(
        "idx_uniq_individual_booking_id",
        table_name="finance_event",
        postgresql_where=sa.text("status IN ('pending', 'ready')"),
    )
