"""add_demarche_simplifiee_id_for_user

Revision ID: 83132c357143
Revises: 67307cd6ee1b
Create Date: 2019-06-12 12:05:06.436132

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "83132c357143"
down_revision = "67307cd6ee1b"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("demarcheSimplifieeApplicationId", sa.BigInteger, nullable=True))


def downgrade():
    op.drop_column("user", "demarcheSimplifieeApplicationId")
