"""Create index on product's ISBN
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "3cb2b2fb88d3"
down_revision = "c86504df1384"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS product_expr_idx ON product (("extraData" ->> 'isbn'::text))
        """
    )


def downgrade() -> None:
    op.drop_index(op.f("product_expr_idx"), table_name="product")
