"""add_provider_parallel_sync
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ee836a8a56e3"
down_revision = "fb3966303e2e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "provider",
        sa.Column("enableParallelSynchronization", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("provider", "enableParallelSynchronization")
