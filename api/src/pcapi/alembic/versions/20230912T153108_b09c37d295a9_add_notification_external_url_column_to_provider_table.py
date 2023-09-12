"""
add notification external url column to provider
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b09c37d295a9"
down_revision = "cecf1fb49589"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("provider", sa.Column("notificationExternalUrl", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("provider", "notificationExternalUrl")
