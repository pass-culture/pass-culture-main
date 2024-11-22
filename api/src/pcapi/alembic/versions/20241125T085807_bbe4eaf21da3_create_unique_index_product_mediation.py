"""Create unique index product_mediation.uuid"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "bbe4eaf21da3"
down_revision = "15b6b1abc8f1"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("COMMIT;")
    op.execute(
        """ CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS "ix_product_mediation_uuid" ON "product_mediation" USING btree (uuid); """
    )
    op.execute("BEGIN;")


def downgrade() -> None:
    op.execute("COMMIT;")
    op.execute(""" DROP INDEX CONCURRENTLY IF EXISTS "ix_product_mediation_uuid" """)
    op.execute("BEGIN;")
