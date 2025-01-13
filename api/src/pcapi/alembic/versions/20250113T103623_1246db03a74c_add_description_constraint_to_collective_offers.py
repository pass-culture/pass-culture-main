"""
Add description constraint to collective offers
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1246db03a74c"
down_revision = "2ef0dd81b7c6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "collective_offer" DROP CONSTRAINT IF EXISTS "collective_offer_description_constraint";
        ALTER TABLE "collective_offer" ADD CONSTRAINT "collective_offer_description_constraint" CHECK (length(description) <= 1500) NOT VALID;
        """
    )

    op.execute(
        """
        ALTER TABLE "collective_offer_template" DROP CONSTRAINT IF EXISTS "collective_offer_tmpl_description_constraint";
        ALTER TABLE "collective_offer_template" ADD CONSTRAINT "collective_offer_tmpl_description_constraint" CHECK (length(description) <= 1500) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("collective_offer_tmpl_description_constraint", table_name="collective_offer_template")
    op.drop_constraint("collective_offer_description_constraint", table_name="collective_offer")
