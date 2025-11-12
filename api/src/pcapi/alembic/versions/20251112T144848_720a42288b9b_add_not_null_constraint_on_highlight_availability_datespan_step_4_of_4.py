"""Add NOT NULL constraint on "highlight.availability_datespan" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "720a42288b9b"
down_revision = "e25d813658b8"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("highlight_availability_datespan_not_null_constraint", table_name="highlight")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "highlight" ADD CONSTRAINT "highlight_availability_datespan_not_null_constraint" CHECK ("availability_datespan" IS NOT NULL) NOT VALID"""
    )
