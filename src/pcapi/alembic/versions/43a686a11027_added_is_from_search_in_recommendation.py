"""Added isFromSearch in Recommendation

Revision ID: 43a686a11027
Revises: 2268bcb671a5
Create Date: 2018-08-30 16:16:15.019889

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "43a686a11027"
down_revision = "ad309156b749"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("recommendation", sa.Column("search", sa.VARCHAR(300), nullable=True))


def downgrade():
    pass
