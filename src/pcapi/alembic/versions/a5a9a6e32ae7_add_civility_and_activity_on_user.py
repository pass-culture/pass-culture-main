"""add_civility_and_activity_on_user

Revision ID: a5a9a6e32ae7
Revises: 8e1f487e2d23
Create Date: 2019-08-13 09:40:07.560188

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a5a9a6e32ae7"
down_revision = "8e1f487e2d23"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("civility", sa.String(20), nullable=True))
    op.add_column("user", sa.Column("activity", sa.String(128), nullable=True))


def downgrade():
    op.drop_column("user", "civility")
    op.drop_column("user", "activity")
