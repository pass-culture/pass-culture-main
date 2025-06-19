"""Add NOT NULL constraint on "chronicle.productIdentifier" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "67104d7ef101"
down_revision = "0d8afa25289b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("chronicle_productIdentifier_not_null_constraint", table_name="chronicle")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "chronicle" ADD CONSTRAINT "chronicle_productIdentifier_not_null_constraint" CHECK ("productIdentifier" IS NOT NULL) NOT VALID"""
    )
