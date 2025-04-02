"""Add NOT NULL constraint on "collective_offer_template.formats" (step 4 of 4)
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d697168fafe0"
down_revision = "f4ae2389f921"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("collective_offer_template_formats_not_null_constraint", table_name="collective_offer_template")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "collective_offer_template" ADD CONSTRAINT "collective_offer_template_formats_not_null_constraint" CHECK ("formats" IS NOT NULL) NOT VALID"""
    )
