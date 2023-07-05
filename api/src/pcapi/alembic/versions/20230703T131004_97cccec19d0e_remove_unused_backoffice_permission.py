"""
Remove 'BATCH_SUSPEND_USERS' permission
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "97cccec19d0e"
down_revision = "ccd0fadcfff1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DELETE FROM permission WHERE name = 'BATCH_SUSPEND_USERS'")


def downgrade() -> None:
    op.execute("INSERT INTO permission (name) VALUES ('BATCH_SUSPEND_USERS')")
