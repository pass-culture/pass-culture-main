"""Delete UserSuspension table
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a93013fc9866"
down_revision = "d3b0bc11c80a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("drop table if exists user_suspension")


def downgrade() -> None:
    pass  # there is no point in restoring the table
