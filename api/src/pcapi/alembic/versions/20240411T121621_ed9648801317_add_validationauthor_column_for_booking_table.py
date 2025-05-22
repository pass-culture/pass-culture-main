"""
add validationAuthor column for Booking table
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from pcapi.core.bookings.models import BookingValidationAuthorType


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ed9648801317"
down_revision = "1c0c3459615b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    booking_author_type = postgresql.ENUM(BookingValidationAuthorType, name="validationAuthorType")
    booking_author_type.create(op.get_bind(), checkfirst=True)
    op.add_column("booking", sa.Column("validationAuthorType", booking_author_type, nullable=True))


def downgrade() -> None:
    op.drop_column("booking", "validationAuthorType")
