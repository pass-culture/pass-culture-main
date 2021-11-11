"""add_is_used_to_token

Revision ID: 5d6f3407546c
Revises: c83abec806af
Create Date: 2021-05-21 12:33:28.285888

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5d6f3407546c"
down_revision = "c83abec806af"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("token", sa.Column("isUsed", sa.Boolean(), server_default=sa.text("false"), nullable=False))


def downgrade():
    op.drop_column("token", "isUsed")
