"""Add NOT NULL constraint on "special_event.endImportDate" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "54e6167683c9"
down_revision = "08346141b0cc"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("special_event_endImportDate_not_null_constraint", table_name="special_event")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "special_event" ADD CONSTRAINT "special_event_endImportDate_not_null_constraint" CHECK ("endImportDate" IS NOT NULL) NOT VALID"""
    )
