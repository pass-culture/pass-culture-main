"""Remove SEARCH_OFFERS permission"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3f4fef666cb4"
down_revision = "515b8245129f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DELETE FROM permission WHERE name = 'SEARCH_OFFERS'")


def downgrade() -> None:
    pass
