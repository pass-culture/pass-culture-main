"""add_externalBookingId_column_to_Booking
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5738a229ef6c"
down_revision = "ce0fcf03be9a"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("booking", sa.Column("externalBookingId", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_booking_externalBookingId"), "booking", ["externalBookingId"], unique=True)
    op.create_foreign_key(None, "booking", "external_booking", ["externalBookingId"], ["id"])


def downgrade():
    op.drop_constraint(None, "booking", type_="foreignkey")
    op.drop_index(op.f("ix_booking_externalBookingId"), table_name="booking")
    op.drop_column("booking", "externalBookingId")
