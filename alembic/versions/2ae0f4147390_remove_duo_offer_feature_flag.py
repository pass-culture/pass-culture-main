"""remove_duo_offer_feature_flag

Revision ID: 2ae0f4147390
Revises: 75f2ccf2be82
Create Date: 2019-12-30 09:01:56.770901

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from models.feature import FeatureToggle

revision = '2ae0f4147390'
down_revision = '75f2ccf2be82'
branch_labels = None
depends_on = None

new_values = ('WEBAPP_SIGNUP', 'FAVORITE_OFFER', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'DUO_OFFER', 'QR_CODE')
previous_values = ('WEBAPP_SIGNUP', 'FAVORITE_OFFER', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE')

previous_enum = sa.Enum(*previous_values, name='duo_featuretoggle')
new_enum = sa.Enum(*new_values, name='duo_featuretoggle')
temporary_enum = sa.Enum(*new_values, name='tmp_duo_featuretoggle')


def upgrade():
    op.execute("DELETE FROM feature WHERE name = 'DUO_OFFER'")

def downgrade():
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE tmp_duo_featuretoggle'
               ' USING name::text::tmp_duo_featuretoggle')
    previous_enum.drop(op.get_bind(), checkfirst=False)
    new_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE duo_featuretoggle'
               ' USING name::text::duo_featuretoggle')
    op.execute("""
            INSERT INTO feature (name, description, "isActive")
            VALUES ('%s', '%s', FALSE);
            """ % (FeatureToggle.DUO_OFFER.name, FeatureToggle.DUO_OFFER.value))
    temporary_enum.drop(op.get_bind(), checkfirst=False)
