"""Add NOT NULL constraint on "special_event.endImportDate" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4a9101c5aa05"
down_revision = "9daf38843ca6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "special_event" DROP CONSTRAINT IF EXISTS "special_event_endImportDate_not_null_constraint";
        ALTER TABLE "special_event" ADD CONSTRAINT "special_event_endImportDate_not_null_constraint" CHECK ("endImportDate" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("special_event_endImportDate_not_null_constraint", table_name="special_event")
