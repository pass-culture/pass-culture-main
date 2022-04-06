"""add_collective_booking_ref_on_pricing_model
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8b8b73636328"
down_revision = "b5d269da9bb3"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("pricing", sa.Column("collectiveBookingId", sa.BigInteger(), nullable=True))
    op.alter_column("pricing", "bookingId", existing_type=sa.BIGINT(), nullable=True)
    op.create_index(op.f("ix_pricing_collectiveBookingId"), "pricing", ["collectiveBookingId"], unique=False)
    op.create_foreign_key(
        "pricing_collective_booking_fkey", "pricing", "collective_booking", ["collectiveBookingId"], ["id"]
    )


def downgrade():
    op.drop_constraint("pricing_collective_booking_fkey", "pricing", type_="foreignkey")
    op.drop_index(op.f("ix_pricing_collectiveBookingId"), table_name="pricing")
    op.alter_column("pricing", "bookingId", existing_type=sa.BIGINT(), nullable=False)
    op.drop_column("pricing", "collectiveBookingId")
