"""drop_offer_type
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7a18546db0d5"
down_revision = "d65f31d992fa"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.execute(
        """
        DROP INDEX CONCURRENTLY IF EXISTS "ix_offer_type"
        """
    )
    op.drop_column("offer", "type")


def downgrade():
    op.add_column("offer", sa.Column("type", sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_offer_type" ON offer ("type")
        """
    )
