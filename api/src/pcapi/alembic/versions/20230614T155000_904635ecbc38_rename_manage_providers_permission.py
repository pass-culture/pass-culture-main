"""Rename permission 'MANAGE_PROVIDERS' into 'ADVANCED_PRO_SUPPORT'
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "904635ecbc38"
down_revision = "29244daf23a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE permission SET name = 'ADVANCED_PRO_SUPPORT' WHERE name = 'MANAGE_PROVIDERS'")


def downgrade() -> None:
    op.execute("UPDATE permission SET name = 'MANAGE_PROVIDERS' WHERE name = 'ADVANCED_PRO_SUPPORT'")
