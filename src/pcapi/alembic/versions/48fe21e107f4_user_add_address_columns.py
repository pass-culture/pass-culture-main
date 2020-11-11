"""user_add_address_columns

Revision ID: 48fe21e107f4
Revises: fbb3ff7f21d3
Create Date: 2020-06-29 08:16:52.684780

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "48fe21e107f4"
down_revision = "fbb3ff7f21d3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user", sa.Column("address", sa.Text, nullable=True))
    op.add_column("user", sa.Column("city", sa.VARCHAR(100), nullable=True))


def downgrade() -> None:
    op.drop_column("user", "city")
    op.drop_column("user", "address")
