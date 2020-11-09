"""add_duo_offer_feature_flag

Revision ID: 914fef4f49ab
Revises: 600464fd8ac8
Create Date: 2019-10-09 12:05:13.610887

"""
from enum import Enum

from alembic import op
import sqlalchemy as sa


class FeatureToggle(Enum):
    DUO_OFFER = 'Permettre la réservation d’une offre pour soi et un accompagnant'


# revision identifiers, used by Alembic.
revision = '914fef4f49ab'
down_revision = '600464fd8ac8'
branch_labels = None
depends_on = None


previous_values = ('WEBAPP_SIGNUP', 'FAVORITE_OFFER', 'DEGRESSIVE_REIMBURSEMENT_RATE')
new_values = ('WEBAPP_SIGNUP', 'FAVORITE_OFFER', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'DUO_OFFER')

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
        """ % (FeatureToggle.DUO_OFFER.name, FeatureToggle.DUO_OFFER.value))
    temporary_enum.drop(op.get_bind(), checkfirst=False)


def downgrade():
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE tmp_featuretoggle'
               ' USING name::text::tmp_featuretoggle')
    new_enum.drop(op.get_bind(), checkfirst=False)
    previous_enum.create(op.get_bind(), checkfirst=False)
    op.execute("DELETE FROM feature WHERE name = 'DUO_OFFER'")
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE featuretoggle'
               ' USING name::text::featuretoggle')
    temporary_enum.drop(op.get_bind(), checkfirst=False)
