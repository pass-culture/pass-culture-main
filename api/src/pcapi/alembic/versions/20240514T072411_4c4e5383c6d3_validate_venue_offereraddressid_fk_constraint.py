"""Validate venue.offererAddressId constraint"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4c4e5383c6d3"
down_revision = "26fdf6be1ace"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute('ALTER TABLE "venue" VALIDATE CONSTRAINT "venue_offererAddressId"')


def downgrade() -> None:
    # Nothing to downgrade
    pass
