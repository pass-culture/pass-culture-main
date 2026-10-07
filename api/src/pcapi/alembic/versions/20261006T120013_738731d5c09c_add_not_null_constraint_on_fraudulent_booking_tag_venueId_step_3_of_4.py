"""Add NOT NULL constraint on "fraudulent_booking_tag.venueId" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "738731d5c09c"
down_revision = "bc8d8220f0fa"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("fraudulent_booking_tag", "venueId", nullable=False)


def downgrade() -> None:
    op.alter_column("fraudulent_booking_tag", "venueId", nullable=True)
