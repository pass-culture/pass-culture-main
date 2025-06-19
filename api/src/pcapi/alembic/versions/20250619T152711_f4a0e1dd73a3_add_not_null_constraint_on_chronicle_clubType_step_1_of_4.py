"""Add NOT NULL constraint on "chronicle.clubType" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "f4a0e1dd73a3"
down_revision = "67104d7ef101"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "chronicle" DROP CONSTRAINT IF EXISTS "chronicle_clubType_not_null_constraint";
        ALTER TABLE "chronicle" ADD CONSTRAINT "chronicle_clubType_not_null_constraint" CHECK ("clubType" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("chronicle_clubType_not_null_constraint", table_name="chronicle")
