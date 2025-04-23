"""Add NOT NULL constraint on "collective_offer_template.formats" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "65f4287d861c"
down_revision = "01dd297a1fc1"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "collective_offer_template" DROP CONSTRAINT IF EXISTS "collective_offer_template_formats_not_null_constraint";
        ALTER TABLE "collective_offer_template" ADD CONSTRAINT "collective_offer_template_formats_not_null_constraint" CHECK ("formats" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("collective_offer_template_formats_not_null_constraint", table_name="collective_offer_template")
