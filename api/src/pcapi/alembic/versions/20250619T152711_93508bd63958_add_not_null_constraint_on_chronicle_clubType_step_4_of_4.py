"""Add NOT NULL constraint on "chronicle.clubType" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "93508bd63958"
down_revision = "d10014c6a975"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("chronicle_clubType_not_null_constraint", table_name="chronicle")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "chronicle" ADD CONSTRAINT "chronicle_clubType_not_null_constraint" CHECK ("clubType" IS NOT NULL) NOT VALID"""
    )
