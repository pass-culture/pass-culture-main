"""drop_is_educational_column
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "fe0d250879b4"
down_revision = "1f778fcd4019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_offer_isEducational", table_name="offer")
    op.drop_column("offer", "isEducational")


def downgrade() -> None:
    op.add_column(
        "offer",
        sa.Column("isEducational", sa.BOOLEAN(), server_default=sa.text("false"), autoincrement=False, nullable=False),
    )
    op.execute(
        """
        COMMIT
        """
    )
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_offer_isEducational" ON offer ("isEducational")
        """
    )
