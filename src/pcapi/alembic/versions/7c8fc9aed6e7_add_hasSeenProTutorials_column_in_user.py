"""add hasSeenProTutorials column for users

Revision ID: 7c8fc9aed6e7
Revises: 514dfbeddddf
Create Date: 2021-02-10 09:23:46.646176

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7c8fc9aed6e7"
down_revision = "514dfbeddddf"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "user", sa.Column("hasSeenProTutorials", sa.Boolean(), nullable=False, server_default=sa.text("false"))
    )


def downgrade():
    op.drop_column("user", "hasSeenProTutorials")
