"""remove_recommendations_with_discovery_and_with_digital_feature_flipping

Revision ID: 44d783e1c855
Revises: 04928427ce14
Create Date: 2020-05-04 16:23:35.528279

"""
import enum

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '44d783e1c855'
down_revision = '04928427ce14'
branch_labels = None
depends_on = None


class FeatureToggle(enum.Enum):
    RECOMMENDATIONS_WITH_DISCOVERY_VIEW = 'Permettre aux utilisateurs d''avoir des recommandations de manière plus rapide'
    RECOMMENDATIONS_WITH_DIGITAL_FIRST = 'Permettre aux bénéficiaires d''avoir des recommendations' \
                                         ' concernant des offres numériques en priorité'


def upgrade():
    new_values = ('WEBAPP_SIGNUP', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE',
                  'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE', 'SEARCH_ALGOLIA', 'SEARCH_LEGACY',
                  'BENEFICIARIES_IMPORT', 'SYNCHRONIZE_ALGOLIA', 'SYNCHRONIZE_ALLOCINE',
                  'SYNCHRONIZE_BANK_INFORMATION', 'SYNCHRONIZE_LIBRAIRES', 'SYNCHRONIZE_TITELIVE',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS', 'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS', 'UPDATE_DISCOVERY_VIEW', 'UPDATE_BOOKING_USED',
                  'RECOMMENDATIONS_WITH_GEOLOCATION', 'NEW_RIBS_UPLOAD', 'SAVE_SEEN_OFFERS', 'BOOKINGS_V2')

    previous_values = ('WEBAPP_SIGNUP', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE',
                       'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE', 'SEARCH_ALGOLIA', 'SEARCH_LEGACY',
                       'BENEFICIARIES_IMPORT', 'SYNCHRONIZE_ALGOLIA', 'SYNCHRONIZE_ALLOCINE',
                       'SYNCHRONIZE_BANK_INFORMATION', 'SYNCHRONIZE_LIBRAIRES', 'SYNCHRONIZE_TITELIVE',
                       'SYNCHRONIZE_TITELIVE_PRODUCTS', 'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
                       'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS', 'UPDATE_DISCOVERY_VIEW', 'UPDATE_BOOKING_USED',
                       'RECOMMENDATIONS_WITH_DISCOVERY_VIEW', 'RECOMMENDATIONS_WITH_DIGITAL_FIRST',
                       'RECOMMENDATIONS_WITH_GEOLOCATION', 'NEW_RIBS_UPLOAD', 'SAVE_SEEN_OFFERS', 'BOOKINGS_V2')

    previous_enum = sa.Enum(*previous_values, name='featuretoggle')
    new_enum = sa.Enum(*new_values, name='featuretoggle')
    temporary_enum = sa.Enum(*new_values, name='tmp_featuretoggle')

    op.execute("DELETE FROM feature "
               "WHERE name IN ('RECOMMENDATIONS_WITH_DISCOVERY_VIEW', 'RECOMMENDATIONS_WITH_DIGITAL_FIRST')")
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE tmp_featuretoggle'
               ' USING name::text::tmp_featuretoggle')
    previous_enum.drop(op.get_bind(), checkfirst=False)
    new_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE featuretoggle'
               ' USING name::text::featuretoggle')
    temporary_enum.drop(op.get_bind(), checkfirst=False)


def downgrade():
    new_values = ('WEBAPP_SIGNUP', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE',
                  'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE', 'SEARCH_ALGOLIA', 'SEARCH_LEGACY',
                  'BENEFICIARIES_IMPORT', 'SYNCHRONIZE_ALGOLIA', 'SYNCHRONIZE_ALLOCINE',
                  'SYNCHRONIZE_BANK_INFORMATION', 'SYNCHRONIZE_LIBRAIRES', 'SYNCHRONIZE_TITELIVE',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS', 'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS', 'UPDATE_DISCOVERY_VIEW', 'UPDATE_BOOKING_USED',
                  'RECOMMENDATIONS_WITH_DISCOVERY_VIEW', 'RECOMMENDATIONS_WITH_DIGITAL_FIRST',
                  'RECOMMENDATIONS_WITH_GEOLOCATION', 'NEW_RIBS_UPLOAD', 'SAVE_SEEN_OFFERS', 'BOOKINGS_V2')

    previous_values = ('WEBAPP_SIGNUP', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE',
                       'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE', 'SEARCH_ALGOLIA', 'SEARCH_LEGACY',
                       'BENEFICIARIES_IMPORT', 'SYNCHRONIZE_ALGOLIA', 'SYNCHRONIZE_ALLOCINE',
                       'SYNCHRONIZE_BANK_INFORMATION', 'SYNCHRONIZE_LIBRAIRES', 'SYNCHRONIZE_TITELIVE',
                       'SYNCHRONIZE_TITELIVE_PRODUCTS', 'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
                       'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS', 'UPDATE_DISCOVERY_VIEW', 'UPDATE_BOOKING_USED',
                       'RECOMMENDATIONS_WITH_GEOLOCATION','NEW_RIBS_UPLOAD', 'SAVE_SEEN_OFFERS', 'BOOKINGS_V2')

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
                VALUES ('%s', '%s', FALSE), ('%s', '%s', FALSE);
                """ % (FeatureToggle.RECOMMENDATIONS_WITH_DISCOVERY_VIEW.name, FeatureToggle.RECOMMENDATIONS_WITH_DISCOVERY_VIEW.value,
                       FeatureToggle.RECOMMENDATIONS_WITH_DIGITAL_FIRST.name, FeatureToggle.RECOMMENDATIONS_WITH_DIGITAL_FIRST.value))
    temporary_enum.drop(op.get_bind(), checkfirst=False)
