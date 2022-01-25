"""deposit unique index on ("userId", "type")
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "dc678612fef4"
down_revision = "1c78fd29dcf6"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.execute(
        """
        CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS "ix_user_type" ON deposit ("userId", "type")
        """
    )


def downgrade():
    op.drop_index("ix_user_type", table_name="deposit")
