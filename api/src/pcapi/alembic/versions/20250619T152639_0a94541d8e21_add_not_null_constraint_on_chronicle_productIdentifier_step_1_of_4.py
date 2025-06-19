"""Add NOT NULL constraint on "chronicle.productIdentifier" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0a94541d8e21"
down_revision = "184d7e51cc34"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "chronicle" DROP CONSTRAINT IF EXISTS "chronicle_productIdentifier_not_null_constraint";
        ALTER TABLE "chronicle" ADD CONSTRAINT "chronicle_productIdentifier_not_null_constraint" CHECK ("productIdentifier" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("chronicle_productIdentifier_not_null_constraint", table_name="chronicle")
