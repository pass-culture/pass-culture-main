"""Add deposit in booking.
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "dfea3ac0b326"
down_revision = "2ca4b0b05bc6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("booking", sa.Column("depositId", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_booking_depositId"), "booking", ["depositId"], unique=False)
    op.create_foreign_key("booking_depositId_fkey", "booking", "deposit", ["depositId"], ["id"])


def downgrade() -> None:
    op.drop_constraint("booking_depositId_fkey", "booking", type_="foreignkey")
    op.drop_index(op.f("ix_booking_depositId"), table_name="booking")
    op.drop_column("booking", "depositId")
