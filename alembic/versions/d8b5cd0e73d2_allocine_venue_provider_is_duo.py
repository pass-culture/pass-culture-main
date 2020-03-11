"""allocine_venue_provider_is_duo

Revision ID: d8b5cd0e73d2
Revises: b25450206c2b
Create Date: 2020-03-11 13:47:42.938609

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.sql import expression

revision = 'd8b5cd0e73d2'
down_revision = 'b25450206c2b'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'allocine_venue_provider',
        'isDuo',
        server_default=expression.true()
    )


def downgrade():
    op.alter_column(
        'allocine_venue_provider',
        'isDuo',
        server_default=expression.false()
    )
