"""create product_chronicle table"""

import sqlalchemy as sa
from alembic import op


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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("productId", "chronicleId", name="unique_product_chronicle_constraint"),
    )

    op.create_foreign_key(
        "product_chronicle_productId_fkey",
        "product_chronicle",
        "product",
        ["productId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )

    op.execute("COMMIT")
    op.create_index(
        op.f("ix_product_chronicle_chronicleId"),
        "product_chronicle",
        ["chronicleId"],
        unique=False,
        postgresql_concurrently=True,
        if_not_exists=True,
    )
    op.create_index(
        op.f("ix_product_chronicle_productId"),
        "product_chronicle",
        ["productId"],
        unique=False,
        postgresql_concurrently=True,
        if_not_exists=True,
    )
    op.execute("BEGIN")


def downgrade() -> None:
    op.execute("COMMIT")
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
    op.execute("BEGIN")
    op.drop_table("product_chronicle")
