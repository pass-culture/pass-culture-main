"""Add comment to User
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3b2ea23b8cf0"
down_revision = "b2f89508f9e0"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("comment", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("user", "comment")
