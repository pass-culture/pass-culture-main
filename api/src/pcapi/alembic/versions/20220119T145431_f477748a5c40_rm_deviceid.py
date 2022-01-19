"""rm deviceId
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f477748a5c40"
down_revision = "c0aecae92e70"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("user_email_history", "deviceId")


def downgrade():
    op.add_column("user_email_history", sa.Column("deviceId", sa.VARCHAR(), autoincrement=False, nullable=True))
