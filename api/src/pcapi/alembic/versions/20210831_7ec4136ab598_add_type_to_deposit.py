"""add_type_to_deposit

Revision ID: 7ec4136ab598
Revises: d324e17d5314
Create Date: 2021-08-31 13:05:56.051068

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7ec4136ab598"
down_revision = "d324e17d5314"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("deposit", sa.Column("type", sa.String(), server_default="GRANT_18", nullable=False))


def downgrade():
    op.drop_column("deposit", "type")
