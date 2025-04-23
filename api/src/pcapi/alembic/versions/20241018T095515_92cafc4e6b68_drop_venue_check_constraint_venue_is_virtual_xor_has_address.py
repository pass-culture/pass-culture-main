"""Drop useless Venue check constraint"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "92cafc4e6b68"
down_revision = "2d723bb0c686"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("""ALTER TABLE "venue" DROP CONSTRAINT IF EXISTS "check_is_virtual_xor_has_address" """)


def downgrade() -> None:
    pass
