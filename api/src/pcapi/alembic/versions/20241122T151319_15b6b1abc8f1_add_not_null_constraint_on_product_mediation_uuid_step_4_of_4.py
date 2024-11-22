"""
Add NOT NULL constraint on "product_mediation.uuid" (step 4 of 4)
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "15b6b1abc8f1"
down_revision = "657e790a7537"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("product_mediation_uuid_not_null_constraint", table_name="product_mediation")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "product_mediation" ADD CONSTRAINT "product_mediation_uuid_not_null_constraint" CHECK ("uuid" IS NOT NULL) NOT VALID"""
    )
