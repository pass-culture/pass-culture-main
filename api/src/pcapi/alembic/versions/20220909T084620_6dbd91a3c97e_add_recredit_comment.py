"""add_recredit_comment
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "6dbd91a3c97e"
down_revision = "bfa3eb158af2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("recredit", sa.Column("comment", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("recredit", "comment")
