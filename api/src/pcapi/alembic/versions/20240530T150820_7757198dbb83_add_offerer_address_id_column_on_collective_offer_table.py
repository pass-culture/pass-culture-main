"""Add CollectiveOffer.offererAddressId column
"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "7757198dbb83"
down_revision = "0fdfda2e6800"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("""ALTER TABLE "collective_offer" ADD COLUMN IF NOT EXISTS "offererAddressId" BIGINT""")


def downgrade() -> None:
    op.execute("""ALTER TABLE "collective_offer" DROP COLUMN IF EXISTS "offererAddressId" """)
