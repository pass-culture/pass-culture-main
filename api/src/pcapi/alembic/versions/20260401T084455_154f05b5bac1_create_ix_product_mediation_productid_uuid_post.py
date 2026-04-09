"""Create unique index product_mediation_productId_uuid."""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "154f05b5bac1"
down_revision = "d29ada3b234c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_product_mediation_productId_uuid"),
            "product_mediation",
            ["productId", "uuid"],
            unique=True,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_product_mediation_productId_uuid"),
            table_name="product_mediation",
            postgresql_concurrently=True,
            if_exists=True,
        )
