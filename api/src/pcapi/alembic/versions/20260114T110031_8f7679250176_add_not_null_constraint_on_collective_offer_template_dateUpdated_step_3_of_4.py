"""Add NOT NULL constraint on "collective_offer_template.dateUpdated" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8f7679250176"
down_revision = "475edd0dc0ab"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("collective_offer_template", "dateUpdated", nullable=False)


def downgrade() -> None:
    op.alter_column("collective_offer_template", "dateUpdated", nullable=True)
