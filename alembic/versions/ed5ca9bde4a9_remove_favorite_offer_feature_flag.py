"""remove_favorite_offer_feature_flag

Revision ID: ed5ca9bde4a9
Revises: 75f2ccf2be82
Create Date: 2019-12-30 17:38:32.166901

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'ed5ca9bde4a9'
down_revision = '75f2ccf2be82'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DELETE FROM feature WHERE name = 'FAVORITE_OFFER'")


def downgrade():
    op.execute("""
      INSERT INTO feature (name, description, "isActive")
      VALUES ('%s', '%s', FALSE);
      """ % ('FAVORITE_OFFER', 'Permettre aux bénéficiaires d''ajouter des offres en favoris'))

