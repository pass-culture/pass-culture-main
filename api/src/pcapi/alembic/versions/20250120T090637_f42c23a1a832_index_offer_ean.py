"""Create index on offer.ean"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "f42c23a1a832"
down_revision = "2a8bb4a6b2e4"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(
            """
                CREATE INDEX CONCURRENTLY IF NOT EXISTS
                ix_offer_ean ON public.offer USING btree (ean);
            """
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(""" DROP INDEX CONCURRENTLY IF EXISTS "ix_offer_ean" """)
