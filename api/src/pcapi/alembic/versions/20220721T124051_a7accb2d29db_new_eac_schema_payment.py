"""new_eac_schema_payment
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "a7accb2d29db"
down_revision = "801ba453e407"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("payment", sa.Column("collectiveBookingId", sa.BigInteger(), nullable=True))
    op.alter_column("payment", "bookingId", existing_type=sa.BIGINT(), nullable=True)
    op.create_index(op.f("ix_payment_collectiveBookingId"), "payment", ["collectiveBookingId"], unique=False)
    op.create_foreign_key(
        "payment_collective_booking_fk", "payment", "collective_booking", ["collectiveBookingId"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("payment_collective_booking_fk", "payment", type_="foreignkey")
    op.drop_index(op.f("ix_payment_collectiveBookingId"), table_name="payment")
    op.alter_column("payment", "bookingId", existing_type=sa.BIGINT(), nullable=False)
    op.drop_column("payment", "collectiveBookingId")
