"""Delete `collective_booking.bookingId` column
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e0e253e1dca7"
down_revision = "e447c5675466"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("collective_booking", "bookingId")


def downgrade() -> None:
    op.add_column("collective_booking", sa.Column("bookingId", sa.BIGINT(), autoincrement=False, nullable=True))
