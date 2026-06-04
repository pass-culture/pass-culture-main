"""Add column: price_category.label"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "1a73b8c9a364"
down_revision = "fdf1bb1a7de5"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("price_category", sa.Column("label", sa.Text(), nullable=True))
    op.alter_column("price_category", "priceCategoryLabelId", existing_type=sa.BIGINT(), nullable=True)


def downgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.alter_column("price_category", "priceCategoryLabelId", existing_type=sa.BIGINT(), nullable=False)
    op.drop_column("price_category", "label")
