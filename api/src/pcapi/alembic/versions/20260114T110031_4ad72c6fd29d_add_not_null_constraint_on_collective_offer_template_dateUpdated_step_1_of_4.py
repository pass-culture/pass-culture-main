"""Add NOT NULL constraint on "collective_offer_template.dateUpdated" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4ad72c6fd29d"
down_revision = "bba150bb6dab"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "collective_offer_template" DROP CONSTRAINT IF EXISTS "collective_offer_template_dateUpdated_not_null_constraint";
        ALTER TABLE "collective_offer_template" ADD CONSTRAINT "collective_offer_template_dateUpdated_not_null_constraint" CHECK ("dateUpdated" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint(
        "collective_offer_template_dateUpdated_not_null_constraint", table_name="collective_offer_template"
    )
