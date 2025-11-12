"""Add NOT NULL constraint on "highlight.highlight_datespan" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "754f76195e13"
down_revision = "6aeccdd21eeb"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("highlight_highlight_datespan_not_null_constraint", table_name="highlight")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "highlight" ADD CONSTRAINT "highlight_highlight_datespan_not_null_constraint" CHECK ("highlight_datespan" IS NOT NULL) NOT VALID"""
    )
