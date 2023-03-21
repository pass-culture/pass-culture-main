"""add_ean_index_offer
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "061957688845"
down_revision = "9b02e53e8369"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS offer_ean_idx
        ON offer
        USING btree ((("jsonData" ->> 'ean'::text)));
        """
    )


def downgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        DROP INDEX CONCURRENTLY IF EXISTS "offer_ean_idx"
        """
    )
