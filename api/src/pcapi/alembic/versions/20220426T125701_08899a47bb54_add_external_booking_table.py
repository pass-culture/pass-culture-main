"""add_external_booking_table
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "08899a47bb54"
down_revision = "8b8b73636328"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "external_booking",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("bookingId", sa.BigInteger(), nullable=False),
        sa.Column("barcode", sa.String(), nullable=False),
        sa.Column("seat", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["bookingId"],
            ["booking.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_external_booking_bookingId"), "external_booking", ["bookingId"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_external_booking_bookingId"), table_name="external_booking")
    op.drop_table("external_booking")
