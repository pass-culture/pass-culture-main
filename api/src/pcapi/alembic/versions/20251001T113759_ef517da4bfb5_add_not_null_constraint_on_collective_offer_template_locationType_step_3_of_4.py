"""Add NOT NULL constraint on "collective_offer_template.locationType" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ef517da4bfb5"
down_revision = "be3f87ea64b1"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("collective_offer_template", "locationType", nullable=False)


def downgrade() -> None:
    op.alter_column("collective_offer_template", "locationType", nullable=True)
