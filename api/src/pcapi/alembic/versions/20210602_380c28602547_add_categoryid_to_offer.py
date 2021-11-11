"""add categoryId to Offer

Revision ID: 380c28602547
Revises: 3cdaeb21d14d
Create Date: 2021-06-02 15:13:11.577602

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "380c28602547"
down_revision = "a5c58daf6917"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("offer", sa.Column("subcategoryId", sa.BigInteger(), nullable=True))


def downgrade():
    op.drop_column("offer", "subcategoryId")
