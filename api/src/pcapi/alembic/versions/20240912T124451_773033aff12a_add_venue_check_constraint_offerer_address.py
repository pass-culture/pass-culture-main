"""Add check_physical_venue_has_offerer_address constraint on venue"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "773033aff12a"
down_revision = "8523f3e2d7d6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "venue" ADD CONSTRAINT "check_physical_venue_has_offerer_address" CHECK (("isVirtual" IS FALSE AND "offererAddressId" IS NOT NULL) OR ("isVirtual" IS TRUE)) NOT VALID;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE "venue" DROP CONSTRAINT IF EXISTS "check_physical_venue_has_offerer_address"
        """
    )
