"""add_user_isActive

Revision ID: 55bf0bb6c53b
Revises: ef6ec02387a3
Create Date: 2020-12-14 09:55:46.642156

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "55bf0bb6c53b"
down_revision = "ef6ec02387a3"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("isActive", sa.BOOLEAN(), server_default=sa.text("true"), nullable=True))


def downgrade():
    op.drop_column("user", "isActive")
