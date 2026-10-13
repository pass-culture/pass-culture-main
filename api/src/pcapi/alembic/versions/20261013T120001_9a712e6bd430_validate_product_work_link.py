"""Validate and index the product work link after deployment."""

from alembic import op


# pre/post deployment: post
revision = "9a712e6bd430"
down_revision = "869c61cd3a23"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index("ix_product_work_id", "product", ["work_id"], postgresql_concurrently=True, if_not_exists=True)
    op.execute("ALTER TABLE product VALIDATE CONSTRAINT product_work_id_fkey")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index("ix_product_work_id", table_name="product", postgresql_concurrently=True, if_exists=True)
