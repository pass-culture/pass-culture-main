"""Add unique index on (`idAProvider`, `offerId`) in `price_category` table"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "404b3075d1a4"
down_revision = "63fa42fd8352"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            "unique_ix_offer_id_id_at_provider",
            "price_category",
            ["offerId", "idAtProvider"],
            unique=True,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "unique_ix_offer_id_id_at_provider",
            table_name="price_category",
            postgresql_concurrently=True,
            if_exists=True,
        )
