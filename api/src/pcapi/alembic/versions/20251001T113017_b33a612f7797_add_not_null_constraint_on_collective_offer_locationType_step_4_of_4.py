"""Add NOT NULL constraint on "collective_offer.locationType" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b33a612f7797"
down_revision = "1d9891c08fbd"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("collective_offer_locationType_not_null_constraint", table_name="collective_offer")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "collective_offer" ADD CONSTRAINT "collective_offer_locationType_not_null_constraint" CHECK ("locationType" IS NOT NULL) NOT VALID"""
    )
