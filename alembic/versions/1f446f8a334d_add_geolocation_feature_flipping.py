"""add_geolocation_feature_flipping

Revision ID: 1f446f8a334d
Revises: b25450206c2b
Create Date: 2020-03-10 10:00:36.296104

"""
import enum

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1f446f8a334d'
down_revision = 'd8b5cd0e73d2'
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
                       'RECOMMENDATIONS_WITH_DISCOVERY_VIEW')

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
                       'RECOMMENDATIONS_WITH_DISCOVERY_VIEW')

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
                  'RECOMMENDATIONS_WITH_GEOLOCATION')

    previous_enum = sa.Enum(*previous_values, name='featuretoggle')
    new_enum = sa.Enum(*new_values, name='featuretoggle')
    temporary_enum = sa.Enum(*new_values, name='tmp_featuretoggle')

    op.execute("DELETE FROM feature WHERE name = 'RECOMMENDATIONS_WITH_GEOLOCATION'")
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE tmp_featuretoggle'
               ' USING name::text::tmp_featuretoggle')
    previous_enum.drop(op.get_bind(), checkfirst=False)
    new_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE featuretoggle'
               ' USING name::text::featuretoggle')
    temporary_enum.drop(op.get_bind(), checkfirst=False)
