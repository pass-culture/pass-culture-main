"""Create a virtual venue for each offerer, make venue.bookingEmail nullable

Revision ID: 8be876a5e4c3
Revises: 10ea71b5a60b
Create Date: 2018-09-05 07:16:10.762245

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8be876a5e4c3'
down_revision = '10ea71b5a60b'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
    """
      BEGIN TRANSACTION;
        ALTER TABLE venue ALTER COLUMN "bookingEmail" DROP NOT NULL;
        INSERT INTO venue ("name", "isVirtual", "managingOffererId") (SELECT 'Offre en ligne', True, o.id FROM offerer o);
      COMMIT;
    """)


def downgrade():
    pass
