"""delete_individual_bookings_post
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "79a357facba0"
down_revision = "930a602ac1af"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_booking_individualBookingId", table_name="booking")
    op.drop_constraint("booking_individualBookingId_fkey", "booking", type_="foreignkey")
    op.drop_column("booking", "individualBookingId")


def downgrade() -> None:
    op.add_column("booking", sa.Column("individualBookingId", sa.BIGINT(), autoincrement=False, nullable=True))
    op.create_foreign_key(
        "booking_individualBookingId_fkey", "booking", "individual_booking", ["individualBookingId"], ["id"]
    )
    op.create_index("ix_booking_individualBookingId", "booking", ["individualBookingId"], unique=False)
