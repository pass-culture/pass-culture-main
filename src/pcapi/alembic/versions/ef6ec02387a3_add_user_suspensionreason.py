"""Add user.suspensionReason

Revision ID: ef6ec02387a3
Revises: ad5e76920552
Create Date: 2020-12-14 09:29:45.052541

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ef6ec02387a3"
down_revision = "4a5c2acfd867"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("suspensionReason", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("user", "suspensionReason")
