"""Drop check_physical_venue_has_offerer_address constraint"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "5e5e3e71c42c"
down_revision = "8cfc813758b8"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("check_physical_venue_has_offerer_address", table_name="venue")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "venue" ADD CONSTRAINT "check_physical_venue_has_offerer_address" CHECK (((("isVirtual" IS FALSE) AND ("offererAddressId" IS NOT NULL)) OR ("isVirtual" IS TRUE))) NOT VALID"""
    )
