"""Validate check_physical_venue_has_offerer_address"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1b4adaffb16b"
down_revision = "265af0d4682c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("""ALTER TABLE "venue" VALIDATE CONSTRAINT "check_physical_venue_has_offerer_address" """)


def downgrade() -> None:
    # Nothing to do
    pass
