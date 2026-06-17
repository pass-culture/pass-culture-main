"""Add NOT NULL constraint on "price_category.label" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ec0b3454ed61"
down_revision = "9cb77b336a8e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("price_category", "label", nullable=False)


def downgrade() -> None:
    op.alter_column("price_category", "label", nullable=True)
