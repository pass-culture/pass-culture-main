"""Add NOT NULL constraint on "highlight.availability_datespan" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "fd51844b4eac"
down_revision = "99b8d179336d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "highlight" DROP CONSTRAINT IF EXISTS "highlight_availability_datespan_not_null_constraint";
        ALTER TABLE "highlight" ADD CONSTRAINT "highlight_availability_datespan_not_null_constraint" CHECK ("availability_datespan" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("highlight_availability_datespan_not_null_constraint", table_name="highlight")
