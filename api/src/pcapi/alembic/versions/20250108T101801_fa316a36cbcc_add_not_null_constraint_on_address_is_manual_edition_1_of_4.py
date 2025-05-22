"""Add NOT NULL constraint on address."isManualEdition" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "fa316a36cbcc"
down_revision = "47982a2a6cdb"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "address" DROP CONSTRAINT IF EXISTS "is_manual_edition_not_null_constraint";
        ALTER TABLE "address" ADD CONSTRAINT "is_manual_edition_not_null_constraint" CHECK ("isManualEdition" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE address DROP CONSTRAINT IF EXISTS is_manual_edition_not_null_constraint")
