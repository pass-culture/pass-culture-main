"""Add NOT NULL constraint on "venue.isOpenToPublic" (step 5 of 5)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "01ecc63457be"
down_revision = "d0ec4af51870"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("venue_isOpenToPublic_not_null_constraint", table_name="venue")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "venue" ADD CONSTRAINT "venue_isOpenToPublic_not_null_constraint" CHECK ("isOpenToPublic" IS NOT NULL) NOT VALID"""
    )
