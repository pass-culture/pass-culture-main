"""Remove api_key.value column."""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d08bfa402042"
down_revision = "11cfe28f2708"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("api_key", "value")


def downgrade():
    op.add_column("api_key", sa.Column("value", sa.VARCHAR(length=64), autoincrement=False, nullable=True))
    op.create_index("ix_api_key_value", "api_key", ["value"], unique=False)
