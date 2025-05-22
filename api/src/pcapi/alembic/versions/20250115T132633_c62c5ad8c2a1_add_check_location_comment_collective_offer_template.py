"""
Add check constraint on locationComment for collective offer template
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c62c5ad8c2a1"
down_revision = "63dea9f44484"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "collective_offer_template" DROP CONSTRAINT IF EXISTS "collective_offer_tmpl_location_comment_constraint";
        ALTER TABLE "collective_offer_template" ADD CONSTRAINT "collective_offer_tmpl_location_comment_constraint" CHECK ("locationComment" IS NULL OR length("locationComment") <= 200) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("collective_offer_tmpl_location_comment_constraint", table_name="collective_offer_template")
