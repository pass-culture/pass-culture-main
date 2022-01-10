"""Rename invoice.url"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "d71dd05eae76"
down_revision = "7b8966ff7913"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("invoice", "url", new_column_name="token")


def downgrade():
    op.alter_column("invoice", "token", new_column_name="url")
