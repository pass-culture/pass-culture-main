"""Add product ean unique index"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8b624eb5699f"
down_revision = "5509ff7c1d73"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout = '300s'")
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_product_ean"),
            "product",
            ["ean"],
            postgresql_where='("ean" IS NOT NULL)',
            if_not_exists=True,
            unique=True,
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    pass
