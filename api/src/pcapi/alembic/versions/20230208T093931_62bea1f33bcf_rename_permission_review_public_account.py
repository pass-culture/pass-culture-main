"""Rename_permission_REVIEW_PUBLIC_ACCOUNT
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "62bea1f33bcf"
down_revision = "79a357facba0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE permission SET name = 'REVIEW_SUSPEND_USER' WHERE name = 'REVIEW_PUBLIC_ACCOUNT'")


def downgrade() -> None:
    op.execute("UPDATE permission SET name = 'REVIEW_PUBLIC_ACCOUNT' WHERE name = 'REVIEW_SUSPEND_USER'")
