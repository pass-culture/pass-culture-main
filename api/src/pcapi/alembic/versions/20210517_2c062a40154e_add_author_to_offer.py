"""add_author_to_offer

Revision ID: 2c062a40154e
Revises: 865dbe4bec27
Create Date: 2021-05-17 16:05:57.108593

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2c062a40154e"
down_revision = "865dbe4bec27"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("offer", sa.Column("authorId", sa.BigInteger(), nullable=True))
    op.create_foreign_key(None, "offer", "user", ["authorId"], ["id"])


def downgrade():
    op.drop_constraint(None, "offer", type_="foreignkey")
    op.drop_column("offer", "authorId")
