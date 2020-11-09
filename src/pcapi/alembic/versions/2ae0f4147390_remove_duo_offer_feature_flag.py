"""remove_duo_offer_feature_flag

Revision ID: 2ae0f4147390
Revises: 2cb37da9609e
Create Date: 2019-12-30 09:01:56.770901

"""
from enum import Enum

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ae0f4147390'
down_revision = '2cb37da9609e'
branch_labels = None
depends_on = None


class FeatureToggle(Enum):
    DUO_OFFER = 'Permettre la réservation d’une offre pour soi et un accompagnant'


def upgrade():
    new_values = ('WEBAPP_SIGNUP', 'FAVORITE_OFFER', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE', 'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE')
    previous_values = ('WEBAPP_SIGNUP', 'FAVORITE_OFFER', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'DUO_OFFER', 'QR_CODE', 'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE')

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
    new_values = ('WEBAPP_SIGNUP', 'FAVORITE_OFFER', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'DUO_OFFER', 'QR_CODE', 'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE')
    previous_values = ('WEBAPP_SIGNUP', 'FAVORITE_OFFER', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE', 'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE')

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
                """ % (FeatureToggle.DUO_OFFER.name, FeatureToggle.DUO_OFFER.value))
    temporary_enum.drop(op.get_bind(), checkfirst=False)
