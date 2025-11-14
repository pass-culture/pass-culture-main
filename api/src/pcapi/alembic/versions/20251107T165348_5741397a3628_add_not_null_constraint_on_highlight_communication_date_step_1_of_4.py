"""Add NOT NULL constraint on "highlight.communication_date" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "5741397a3628"
down_revision = "8er652fgki52"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "highlight" DROP CONSTRAINT IF EXISTS "highlight_communication_date_not_null_constraint";
        ALTER TABLE "highlight" ADD CONSTRAINT "highlight_communication_date_not_null_constraint" CHECK ("communication_date" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("highlight_communication_date_not_null_constraint", if_exists=True, table_name="highlight")
