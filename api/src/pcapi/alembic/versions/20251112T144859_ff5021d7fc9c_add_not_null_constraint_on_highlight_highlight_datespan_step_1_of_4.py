"""Add NOT NULL constraint on "highlight.highlight_datespan" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ff5021d7fc9c"
down_revision = "720a42288b9b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "highlight" DROP CONSTRAINT IF EXISTS "highlight_highlight_datespan_not_null_constraint";
        ALTER TABLE "highlight" ADD CONSTRAINT "highlight_highlight_datespan_not_null_constraint" CHECK ("highlight_datespan" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("highlight_highlight_datespan_not_null_constraint", table_name="highlight")
