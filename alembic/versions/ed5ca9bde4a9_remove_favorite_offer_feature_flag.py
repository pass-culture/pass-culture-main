"""remove_favorite_offer_feature_flag

Revision ID: ed5ca9bde4a9
Revises: 75f2ccf2be82
Create Date: 2019-12-30 17:38:32.166901

"""
from enum import Enum
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ed5ca9bde4a9'
down_revision = '75f2ccf2be82'
branch_labels = None
depends_on = None

class FeatureToggle(Enum):
    WEBAPP_SIGNUP = 'Permettre aux bénéficiaires de créer un compte'
    FAVORITE_OFFER = 'Permettre aux bénéficiaires d''ajouter des offres en favoris'
    DEGRESSIVE_REIMBURSEMENT_RATE = 'Permettre le remboursement avec un barème dégressif par lieu'
    QR_CODE = 'Permettre la validation d''une contremarque via QR code'


def upgrade():
    op.execute("DELETE FROM feature WHERE name = 'FAVORITE_OFFER'")

    new_values = ('WEBAPP_SIGNUP', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE')
    previous_values = ('WEBAPP_SIGNUP', 'FAVORITE_OFFER', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE')

    op.execute("DELETE FROM feature WHERE name = 'DUO_OFFER'")
    previous_enum = sa.Enum(*previous_values, name='featuretoggle')
    new_enum = sa.Enum(*new_values, name='featuretoggle')
    temporary_enum = sa.Enum(*previous_values, name='tmp_featuretoggle')

    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE TMP_FEATURETOGGLE'
               ' USING name::TEXT::TMP_FEATURETOGGLE')
    previous_enum.drop(op.get_bind(), checkfirst=False)
    new_enum.create(op.get_bind(), checkfirst=False)

    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE FEATURETOGGLE'
               ' USING name::TEXT::FEATURETOGGLE')
    temporary_enum.drop(op.get_bind(), checkfirst=False)


def downgrade():
    new_values = ('WEBAPP_SIGNUP', 'FAVORITE_OFFER', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE')
    previous_values = ('WEBAPP_SIGNUP', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE')

    previous_enum = sa.Enum(*previous_values, name='featuretoggle')
    new_enum = sa.Enum(*new_values, name='featuretoggle')
    temporary_enum = sa.Enum(*new_values, name='tmp_featuretoggle')

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



