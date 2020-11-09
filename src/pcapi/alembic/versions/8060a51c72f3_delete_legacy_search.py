"""delete_legacy_search

Revision ID: 8060a51c72f3
Revises: 25c2e6a4534d
Create Date: 2020-04-15 14:27:10.575871

"""
import enum

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8060a51c72f3'
down_revision = '25c2e6a4534d'
branch_labels = None
depends_on = None


class FeatureToggle(enum.Enum):
    SEARCH_LEGACY = 'Permettre la recherche classique'


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
    op.execute("DELETE FROM feature WHERE name = 'SEARCH_LEGACY'")
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE TMP_FEATURETOGGLE'
               ' USING name::TEXT::TMP_FEATURETOGGLE')
    new_enum.drop(op.get_bind(), checkfirst=False)

    previous_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE FEATURETOGGLE'
               ' USING name::TEXT::FEATURETOGGLE')
    temporary_enum.drop(op.get_bind(), checkfirst=False)


def downgrade():
    previous_values = ('BENEFICIARIES_IMPORT',
                       'DEGRESSIVE_REIMBURSEMENT_RATE',
                       'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE',
                       'QR_CODE',
                       'SEARCH_ALGOLIA',
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
                  'RECOMMENDATIONS_WITH_GEOLOCATION')

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
                    """ % (FeatureToggle.SEARCH_LEGACY.name, FeatureToggle.SEARCH_LEGACY.value))
    temporary_enum.drop(op.get_bind(), checkfirst=False)
