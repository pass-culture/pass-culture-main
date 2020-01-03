"""remove_duo_offer_feature_flag

Revision ID: 2ae0f4147390
Revises: 75f2ccf2be82
Create Date: 2019-12-30 09:01:56.770901

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '2ae0f4147390'
down_revision = '75f2ccf2be82'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("DELETE FROM feature WHERE name = 'DUO_OFFER'")

def downgrade():
      op.execute("""
      INSERT INTO feature (name, description, "isActive")
      VALUES ('%s', '%s', FALSE);
      """ % ('DUO_OFFER', 'Permettre la réservation d’une offre pour soi et un accompagnant'))
