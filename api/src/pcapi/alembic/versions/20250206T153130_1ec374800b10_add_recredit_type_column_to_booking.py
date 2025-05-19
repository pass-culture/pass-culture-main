"""Add usedRecreditType column to Booking"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.bookings.models import BookingRecreditType
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "1ec374800b10"
down_revision = "2c9f88a4345a"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "booking",
        sa.Column("usedRecreditType", MagicEnum(BookingRecreditType), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("booking", "usedRecreditType")
