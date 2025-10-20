"""Add NOT NULL constraint on "venue.publicName" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "19faaa413a12"
down_revision = "c214a734e583"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("venue_publicName_not_null_constraint", table_name="venue")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "venue" ADD CONSTRAINT "venue_publicName_not_null_constraint" CHECK ("publicName" IS NOT NULL) NOT VALID"""
    )
