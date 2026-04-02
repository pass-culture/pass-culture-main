"""Drop index ix_product_mediation_productId"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "67782b4aafed"
down_revision = "154f05b5bac1"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_product_mediation_productId",
            table_name="product_mediation",
            postgresql_concurrently=True,
            if_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_product_mediation_productId",
            "product_mediation",
            ["productId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
