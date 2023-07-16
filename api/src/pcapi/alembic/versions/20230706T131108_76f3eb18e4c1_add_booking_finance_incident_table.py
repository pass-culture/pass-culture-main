"""
Add `booking_finance_incident` table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "76f3eb18e4c1"
down_revision = "1f2efac36ecf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "booking_finance_incident",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("newTotalAmount", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("booking_finance_incident")
