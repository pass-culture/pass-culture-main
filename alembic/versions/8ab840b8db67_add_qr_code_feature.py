"""add_qr_code_feature

Revision ID: 8ab840b8db67
Revises: eda764ae6b37
Create Date: 2019-10-29 12:57:51.751401

"""
from enum import Enum
from alembic import op
import sqlalchemy as sa

class FeatureToggle(Enum):
    WEBAPP_SIGNUP = 'Permettre aux bénéficiaires de créer un compte'
    FAVORITE_OFFER = 'Permettre aux bénéficiaires d''ajouter des offres en favoris'
    DEGRESSIVE_REIMBURSEMENT_RATE = 'Permettre le remboursement avec un barème dégressif par lieu'
    DUO_OFFER = 'Permettre la réservation d’une offre pour soi et un accompagnant'
    QR_CODE = 'Permettre la validation d''une contremarque via QR code'


# revision identifiers, used by Alembic.
revision = '8ab840b8db67'
down_revision = 'eda764ae6b37'
branch_labels = None
depends_on = None


previous_values = ('WEBAPP_SIGNUP', 'FAVORITE_OFFER', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'DUO_OFFER')
new_values = ('WEBAPP_SIGNUP', 'FAVORITE_OFFER', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'DUO_OFFER', 'QR_CODE')

previous_enum = sa.Enum(*previous_values, name='featuretoggle')
new_enum = sa.Enum(*new_values, name='featuretoggle')
temporary_enum = sa.Enum(*new_values, name='tmp_featuretoggle')


def upgrade():
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
        """ % (FeatureToggle.QR_CODE.name, FeatureToggle.QR_CODE.value))
    temporary_enum.drop(op.get_bind(), checkfirst=False)


def downgrade():
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE tmp_featuretoggle'
               ' USING name::text::tmp_featuretoggle')
    new_enum.drop(op.get_bind(), checkfirst=False)
    previous_enum.create(op.get_bind(), checkfirst=False)
    op.execute("DELETE FROM feature WHERE name = 'QR_CODE'")
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE featuretoggle'
               ' USING name::text::featuretoggle')
    temporary_enum.drop(op.get_bind(), checkfirst=False)
