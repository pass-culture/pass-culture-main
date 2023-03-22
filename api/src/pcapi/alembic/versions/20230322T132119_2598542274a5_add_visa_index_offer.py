"""add_visa_index_offer
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2598542274a5"
down_revision = "474312bd6eaf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS offer_visa_idx
        ON offer
        USING btree ((("jsonData" ->> 'visa'::text)));
        """
    )


def downgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        DROP INDEX CONCURRENTLY IF EXISTS "offer_visa_idx"
        """
    )
