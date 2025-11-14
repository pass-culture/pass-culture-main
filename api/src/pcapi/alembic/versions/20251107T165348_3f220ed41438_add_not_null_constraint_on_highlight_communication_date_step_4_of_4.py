"""Add NOT NULL constraint on "highlight.communication_date" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3f220ed41438"
down_revision = "4eaaf25ffb2b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("highlight_communication_date_not_null_constraint", table_name="highlight")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "highlight" ADD CONSTRAINT "highlight_communication_date_not_null_constraint" CHECK ("communication_date" IS NOT NULL) NOT VALID"""
    )
