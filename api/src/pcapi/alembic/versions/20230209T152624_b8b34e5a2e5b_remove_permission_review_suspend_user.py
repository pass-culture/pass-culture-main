"""Remove_permission_REVIEW_SUSPEND_USER
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b8b34e5a2e5b"
down_revision = "62bea1f33bcf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # REVIEW_SUSPEND_USER was added but never deployed until production
    op.execute("DELETE FROM permission WHERE name = 'REVIEW_SUSPEND_USER'")


def downgrade() -> None:
    pass
