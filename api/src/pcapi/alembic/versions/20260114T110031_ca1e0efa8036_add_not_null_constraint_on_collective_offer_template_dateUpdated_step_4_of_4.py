"""Add NOT NULL constraint on "collective_offer_template.dateUpdated" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ca1e0efa8036"
down_revision = "8f7679250176"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "collective_offer_template_dateUpdated_not_null_constraint", table_name="collective_offer_template"
    )


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "collective_offer_template" ADD CONSTRAINT "collective_offer_template_dateUpdated_not_null_constraint" CHECK ("dateUpdated" IS NOT NULL) NOT VALID"""
    )
