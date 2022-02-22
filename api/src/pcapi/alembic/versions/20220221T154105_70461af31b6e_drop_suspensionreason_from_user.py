"""Drop suspensionReason from User
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "70461af31b6e"
down_revision = "ffafc4d7210f"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("user", "suspensionReason")


def downgrade():
    op.add_column("user", sa.Column("suspensionReason", sa.TEXT(), autoincrement=False, nullable=True))
