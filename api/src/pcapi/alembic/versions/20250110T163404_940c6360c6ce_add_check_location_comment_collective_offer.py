"""
Add check constraint on locationComment for collective offer
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "940c6360c6ce"
down_revision = "bfd459b4a913"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "collective_offer" DROP CONSTRAINT IF EXISTS "collective_offer_location_comment_constraint";
        ALTER TABLE "collective_offer" ADD CONSTRAINT "collective_offer_location_comment_constraint" CHECK ("locationComment" IS NULL OR length("locationComment") <= 200) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("collective_offer_location_comment_constraint", table_name="collective_offer")
