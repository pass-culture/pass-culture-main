"""Add NOT NULL constraint on "chronicle.productIdentifierType" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "184d7e51cc34"
down_revision = "1c3da9462b8c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("chronicle_productIdentifierType_not_null_constraint", table_name="chronicle")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "chronicle" ADD CONSTRAINT "chronicle_productIdentifierType_not_null_constraint" CHECK ("productIdentifierType" IS NOT NULL) NOT VALID"""
    )
