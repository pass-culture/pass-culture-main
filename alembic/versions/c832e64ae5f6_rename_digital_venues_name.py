"""rename digital venues name

Revision ID: c832e64ae5f6
Revises: 47576c4aecc3
Create Date: 2019-09-18 09:21:55.389861

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c832e64ae5f6'
down_revision = '47576c4aecc3'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
            UPDATE venue
            SET "name"=REPLACE("name", 'Offre en ligne', 'Offre numérique')
            WHERE "name" LIKE '%Offre en ligne%';
            """)


def downgrade():
    op.execute("""
            UPDATE venue
            SET "name"=REPLACE("name", 'Offre numérique', 'Offre en ligne')
            WHERE "name" LIKE '%Offre numérique%';
            """)