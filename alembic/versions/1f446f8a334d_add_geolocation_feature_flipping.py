"""add_geolocation_feature_flipping

Revision ID: 1f446f8a334d
Revises: 9366fb8f8fe9
Create Date: 2020-03-10 10:00:36.296104

"""
import enum

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '1f446f8a334d'
down_revision = '9366fb8f8fe9'
branch_labels = None
depends_on = None


class FeatureToggle(enum.Enum):
    RECOMMENDATIONS_WITH_GEOLOCATION = 'Permettre aux utilisateurs d''avoir accès aux offres à 100km de leur position'


def upgrade():
    previous_values = ('BENEFICIARIES_IMPORT',
                       'DEGRESSIVE_REIMBURSEMENT_RATE',
                       'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE',
                       'QR_CODE',
                       'SEARCH_ALGOLIA',
                       'SEARCH_LEGACY',
                       'SYNCHRONIZE_ALGOLIA',
                       'SYNCHRONIZE_ALLOCINE',
                       'SYNCHRONIZE_BANK_INFORMATION',
                       'SYNCHRONIZE_LIBRAIRES',
                       'SYNCHRONIZE_TITELIVE',
                       'SYNCHRONIZE_TITELIVE_PRODUCTS',
                       'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
                       'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS',
                       'UPDATE_DISCOVERY_VIEW',
                       'UPDATE_BOOKING_USED',
                       'WEBAPP_SIGNUP',
                       'RECOMMENDATIONS_WITH_DISCOVERY_VIEW',
                       'RECOMMENDATIONS_WITH_DIGITAL_FIRST')

    new_values = ('BENEFICIARIES_IMPORT',
                  'DEGRESSIVE_REIMBURSEMENT_RATE',
                  'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE',
                  'QR_CODE',
                  'SEARCH_ALGOLIA',
                  'SEARCH_LEGACY',
                  'SYNCHRONIZE_ALGOLIA',
                  'SYNCHRONIZE_ALLOCINE',
                  'SYNCHRONIZE_BANK_INFORMATION',
                  'SYNCHRONIZE_LIBRAIRES',
                  'SYNCHRONIZE_TITELIVE',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS',
                  'UPDATE_DISCOVERY_VIEW',
                  'UPDATE_BOOKING_USED',
                  'WEBAPP_SIGNUP',
                  'RECOMMENDATIONS_WITH_DISCOVERY_VIEW',
                  'RECOMMENDATIONS_WITH_DIGITAL_FIRST',
                  'RECOMMENDATIONS_WITH_GEOLOCATION')

    previous_enum = sa.Enum(*previous_values, name='featuretoggle')
    new_enum = sa.Enum(*new_values, name='featuretoggle')
    temporary_enum = sa.Enum(*new_values, name='tmp_featuretoggle')

    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE TMP_FEATURETOGGLE'
               ' USING name::TEXT::TMP_FEATURETOGGLE')
    previous_enum.drop(op.get_bind(), checkfirst=False)
    new_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE FEATURETOGGLE'
               ' USING name::TEXT::FEATURETOGGLE')
    op.execute("""
        INSERT INTO feature (name, description, "isActive")
        VALUES ('%s', '%s', FALSE);
        """ % (
        FeatureToggle.RECOMMENDATIONS_WITH_GEOLOCATION.name, FeatureToggle.RECOMMENDATIONS_WITH_GEOLOCATION.value))
    temporary_enum.drop(op.get_bind(), checkfirst=False)


def downgrade():
    previous_values = ('BENEFICIARIES_IMPORT',
                       'DEGRESSIVE_REIMBURSEMENT_RATE',
                       'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE',
                       'QR_CODE',
                       'SEARCH_ALGOLIA',
                       'SEARCH_LEGACY',
                       'SYNCHRONIZE_ALGOLIA',
                       'SYNCHRONIZE_ALLOCINE',
                       'SYNCHRONIZE_BANK_INFORMATION',
                       'SYNCHRONIZE_LIBRAIRES',
                       'SYNCHRONIZE_TITELIVE',
                       'SYNCHRONIZE_TITELIVE_PRODUCTS',
                       'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
                       'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS',
                       'UPDATE_DISCOVERY_VIEW',
                       'UPDATE_BOOKING_USED',
                       'WEBAPP_SIGNUP',
                       'RECOMMENDATIONS_WITH_DISCOVERY_VIEW',
                       'RECOMMENDATIONS_WITH_DIGITAL_FIRST')

    new_values = ('BENEFICIARIES_IMPORT',
                  'DEGRESSIVE_REIMBURSEMENT_RATE',
                  'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE',
                  'QR_CODE',
                  'SEARCH_ALGOLIA',
                  'SEARCH_LEGACY',
                  'SYNCHRONIZE_ALGOLIA',
                  'SYNCHRONIZE_ALLOCINE',
                  'SYNCHRONIZE_BANK_INFORMATION',
                  'SYNCHRONIZE_LIBRAIRES',
                  'SYNCHRONIZE_TITELIVE',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS',
                  'UPDATE_DISCOVERY_VIEW',
                  'UPDATE_BOOKING_USED',
                  'WEBAPP_SIGNUP',
                  'RECOMMENDATIONS_WITH_DISCOVERY_VIEW',
                  'RECOMMENDATIONS_WITH_DIGITAL_FIRST',
                  'RECOMMENDATIONS_WITH_GEOLOCATION')

    previous_enum = sa.Enum(*previous_values, name='featuretoggle')
    new_enum = sa.Enum(*new_values, name='featuretoggle')
    temporary_enum = sa.Enum(*new_values, name='tmp_featuretoggle')

    op.execute("DELETE FROM feature WHERE name = 'RECOMMENDATIONS_WITH_GEOLOCATION'")
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE TMP_FEATURETOGGLE'
               ' USING name::TEXT::TMP_FEATURETOGGLE')
    previous_enum.drop(op.get_bind(), checkfirst=False)
    new_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE FEATURETOGGLE'
               ' USING name::TEXT::FEATURETOGGLE')
    temporary_enum.drop(op.get_bind(), checkfirst=False)
