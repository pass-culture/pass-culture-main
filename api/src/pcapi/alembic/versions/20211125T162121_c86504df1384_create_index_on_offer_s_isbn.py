"""Create index on offer's ISBN
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "c86504df1384"
down_revision = "91827317eb25"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    # Since the index is quite long to create, we'll create it manually.
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS offer_expr_idx ON offer (("extraData" ->> 'isbn'::text))
        """
    )


def downgrade() -> None:
    op.drop_index(op.f("offer_expr_idx"), table_name="offer")
