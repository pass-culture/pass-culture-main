"""
Add NOT NULL constraint on "product_mediation.uuid" (step 1 of 4)
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "eea52af556f7"
down_revision = "ddb791b7e221"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "product_mediation" DROP CONSTRAINT IF EXISTS "product_mediation_uuid_not_null_constraint";
        ALTER TABLE "product_mediation" ADD CONSTRAINT "product_mediation_uuid_not_null_constraint" CHECK ("uuid" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("product_mediation_uuid_not_null_constraint", table_name="product_mediation")
