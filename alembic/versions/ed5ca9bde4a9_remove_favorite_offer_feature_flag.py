"""remove_favorite_offer_feature_flag

Revision ID: ed5ca9bde4a9
Revises: 2ae0f4147390
Create Date: 2019-12-30 17:38:32.166901

"""
from enum import Enum
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ed5ca9bde4a9'
down_revision = '2ae0f4147390'
branch_labels = None
depends_on = None

class FeatureToggle(Enum):
    FAVORITE_OFFER = 'Permettre aux bénéficiaires d''ajouter des offres en favoris'

previous_values = ('WEBAPP_SIGNUP', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE',
                  'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE')

new_values = ('WEBAPP_SIGNUP', 'FAVORITE_OFFER', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE',
                       'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE')

previous_enum = sa.Enum(*previous_values, name='featuretoggle')
new_enum = sa.Enum(*new_values, name='featuretoggle')
temporary_enum = sa.Enum(*new_values, name='tmp_featuretoggle')

def upgrade():
    op.execute("DELETE FROM feature WHERE name = 'FAVORITE_OFFER'")
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE TMP_FEATURETOGGLE'
               ' USING name::TEXT::TMP_FEATURETOGGLE')
    new_enum.drop(op.get_bind(), checkfirst=False)

    previous_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE FEATURETOGGLE'
               ' USING name::TEXT::FEATURETOGGLE')
    temporary_enum.drop(op.get_bind(), checkfirst=False)


def downgrade():
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE tmp_featuretoggle'
               ' USING name::text::tmp_featuretoggle')
    previous_enum.drop(op.get_bind(), checkfirst=False)
    new_enum.create(op.get_bind(), checkfirst=False)

    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE featuretoggle'
               ' USING name::text::featuretoggle')
    op.execute("""
                INSERT INTO feature (name, description, "isActive")
                VALUES ('%s', '%s', FALSE);
                """ % (FeatureToggle.FAVORITE_OFFER.name, FeatureToggle.FAVORITE_OFFER.value))
    temporary_enum.drop(op.get_bind(), checkfirst=False)
