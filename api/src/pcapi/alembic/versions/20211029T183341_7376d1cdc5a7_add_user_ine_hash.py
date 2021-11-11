"""add_user_ine_hash
"""
from alembic import op
import sqlalchemy as sa


revision = "7376d1cdc5a7"
down_revision = "4584c4d37792"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("ineHash", sa.Text(), nullable=True))
    op.create_unique_constraint(None, "user", ["ineHash"])


def downgrade():
    op.drop_column("user", "ineHash")
