"""add_feature_flipping_for_recommendations_v1

Revision ID: d6206bae00b6
Revises: 85af82acac13
Create Date: 2020-03-31 09:19:37.380859

"""
import enum

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd6206bae00b6'
down_revision = '85af82acac13'
branch_labels = None
depends_on = None


class FeatureToggle(enum.Enum):
    RECOMMENDATIONS = 'Permettre aux utilisateurs d''avoir des recommandations'


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
                       'RECOMMENDATIONS_WITH_DIGITAL_FIRST',
                       'RECOMMENDATIONS_WITH_GEOLOCATION')

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
                  'RECOMMENDATIONS_WITH_GEOLOCATION',
                  'RECOMMENDATIONS')

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
        VALUES ('%s', '%s', TRUE);
        """ % (
        FeatureToggle.RECOMMENDATIONS.name, FeatureToggle.RECOMMENDATIONS.value))
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
                       'RECOMMENDATIONS_WITH_DIGITAL_FIRST',
                       'RECOMMENDATIONS_WITH_GEOLOCATION')

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
                  'RECOMMENDATIONS_WITH_GEOLOCATION',
                  'RECOMMENDATIONS')

    previous_enum = sa.Enum(*previous_values, name='featuretoggle')
    new_enum = sa.Enum(*new_values, name='featuretoggle')
    temporary_enum = sa.Enum(*new_values, name='tmp_featuretoggle')

    op.execute("DELETE FROM feature WHERE name = 'RECOMMENDATIONS'")
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE TMP_FEATURETOGGLE'
               ' USING name::TEXT::TMP_FEATURETOGGLE')
    previous_enum.drop(op.get_bind(), checkfirst=False)
    new_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE FEATURETOGGLE'
               ' USING name::TEXT::FEATURETOGGLE')
    temporary_enum.drop(op.get_bind(), checkfirst=False)
