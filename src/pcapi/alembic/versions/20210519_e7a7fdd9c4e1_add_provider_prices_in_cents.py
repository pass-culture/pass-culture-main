"""Add `Provider.pricesInCents`

Revision ID: e7a7fdd9c4e1
Revises: 40afbb732e70
Create Date: 2021-05-19 14:02:45.358481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e7a7fdd9c4e1"
down_revision = "40afbb732e70"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("provider", sa.Column("pricesInCents", sa.Boolean(), server_default=sa.text("false"), nullable=False))


def downgrade():
    op.drop_column("provider", "pricesInCents")
