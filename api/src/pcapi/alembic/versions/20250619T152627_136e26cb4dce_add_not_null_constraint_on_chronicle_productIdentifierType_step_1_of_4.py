"""Add NOT NULL constraint on "chronicle.productIdentifierType" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "136e26cb4dce"
down_revision = "30eed30cc8e8"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "chronicle" DROP CONSTRAINT IF EXISTS "chronicle_productIdentifierType_not_null_constraint";
        ALTER TABLE "chronicle" ADD CONSTRAINT "chronicle_productIdentifierType_not_null_constraint" CHECK ("productIdentifierType" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("chronicle_productIdentifierType_not_null_constraint", table_name="chronicle")
