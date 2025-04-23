"""Add unique constraint on (`idAtProvider`,`offerId`) in `price_category` table."""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d0a81150dd8d"
down_revision = "da2896f47266"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    # Should be executed quickly as we are using an index
    op.execute(
        """
        ALTER TABLE "price_category" ADD CONSTRAINT "unique_offer_id_id_at_provider" UNIQUE USING INDEX "unique_ix_offer_id_id_at_provider"
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE "price_category" DROP CONSTRAINT IF EXISTS "unique_offer_id_id_at_provider";
        """
    )
    # `COMMIT` and isolation of the `CREATE UNIQUE INDEX CONCURRENTLY` command necessary since it cannot run in a transaction block
    with op.get_context().autocommit_block():
        op.create_index(
            "unique_ix_offer_id_id_at_provider",
            "price_category",
            ["offerId", "idAtProvider"],
            unique=True,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
