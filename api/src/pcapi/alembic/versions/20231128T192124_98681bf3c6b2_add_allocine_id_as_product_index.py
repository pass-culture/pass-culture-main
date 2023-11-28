"""Create index on extraData["allocineId"] for the table "Product"
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "98681bf3c6b2"
down_revision = "34eb58880f79"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.create_index(
        "product_allocineId_idx",
        "product",
        [sa.text("(\"jsonData\" -> 'allocineId')")],
        unique=True,
        postgresql_where=sa.text("(\"jsonData\" -> 'allocineId') IS NOT NULL"),
        postgresql_concurrently=True,
    )


def downgrade() -> None:
    op.drop_index(
        "product_allocineId_idx",
        table_name="product",
        postgresql_where=sa.text("(\"jsonData\" -> 'allocineId') IS NOT NULL"),
    )
