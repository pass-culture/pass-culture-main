"""add_expiration_date_on_deposit

Revision ID: 3bf0e437edb0
Revises: 7994bf86faea
Create Date: 2021-02-08 09:07:14.217608

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3bf0e437edb0"
down_revision = "7994bf86faea"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("deposit", sa.Column("expirationDate", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("deposit", "expirationDate")
