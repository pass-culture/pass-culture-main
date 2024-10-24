"""create product_chronicle table
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "cbf6f244c14c"
down_revision = "049490d79544"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "product_chronicle",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("productId", sa.BigInteger(), nullable=False),
        sa.Column("chronicleId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["chronicleId"], ["chronicle.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["productId"], ["product.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("productId", "chronicleId", name="unique_product_chronicle_constraint"),
    )
    op.create_index(op.f("ix_product_chronicle_chronicleId"), "product_chronicle", ["chronicleId"], unique=False)
    op.create_index(op.f("ix_product_chronicle_productId"), "product_chronicle", ["productId"], unique=False)


def downgrade() -> None:
    op.drop_index(
        op.f("ix_product_chronicle_productId"),
        table_name="product_chronicle",
        postgresql_concurrently=True,
        if_exists=True,
    )
    op.drop_index(
        op.f("ix_product_chronicle_chronicleId"),
        table_name="product_chronicle",
        postgresql_concurrently=True,
        if_exists=True,
    )
    op.drop_table("product_chronicle")
