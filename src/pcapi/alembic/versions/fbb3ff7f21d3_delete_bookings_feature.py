"""delete_bookings_feature

Revision ID: fbb3ff7f21d3
Revises: 0fce064a0f84
Create Date: 2020-06-26 08:59:48.001790

"""
import enum

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fbb3ff7f21d3'
down_revision = '0fce064a0f84'
branch_labels = None
depends_on = None


class FeatureToggle(enum.Enum):
    BOOKINGS_V2 = 'Permettre d''afficher la nouvelle visualisation des réservations d''un offreur'


def upgrade():
    old_values = ('WEBAPP_SIGNUP', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE',
                  'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE', 'SEARCH_ALGOLIA', 'SEARCH_LEGACY',
                  'BENEFICIARIES_IMPORT', 'SYNCHRONIZE_ALGOLIA', 'SYNCHRONIZE_ALLOCINE',
                  'SYNCHRONIZE_BANK_INFORMATION', 'SYNCHRONIZE_LIBRAIRES', 'SYNCHRONIZE_TITELIVE',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS', 'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS', 'UPDATE_DISCOVERY_VIEW', 'UPDATE_BOOKING_USED',
                  'RECOMMENDATIONS_WITH_DISCOVERY_VIEW', 'RECOMMENDATIONS_WITH_DIGITAL_FIRST',
                  'RECOMMENDATIONS_WITH_GEOLOCATION', 'NEW_RIBS_UPLOAD', 'SAVE_SEEN_OFFERS', 'BOOKINGS_V2',
                  'API_SIRENE_AVAILABLE', 'CLEAN_DISCOVERY_VIEW')

    new_values = ('WEBAPP_SIGNUP', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE',
                  'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE', 'SEARCH_ALGOLIA', 'SEARCH_LEGACY',
                  'BENEFICIARIES_IMPORT', 'SYNCHRONIZE_ALGOLIA', 'SYNCHRONIZE_ALLOCINE',
                  'SYNCHRONIZE_BANK_INFORMATION', 'SYNCHRONIZE_LIBRAIRES', 'SYNCHRONIZE_TITELIVE',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS', 'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS', 'UPDATE_DISCOVERY_VIEW', 'UPDATE_BOOKING_USED',
                  'RECOMMENDATIONS_WITH_DISCOVERY_VIEW', 'RECOMMENDATIONS_WITH_DIGITAL_FIRST',
                  'RECOMMENDATIONS_WITH_GEOLOCATION', 'NEW_RIBS_UPLOAD', 'SAVE_SEEN_OFFERS', 'API_SIRENE_AVAILABLE',
                  'CLEAN_DISCOVERY_VIEW')

    op.execute("DELETE FROM feature WHERE name = '%s'" % FeatureToggle.BOOKINGS_V2.name)

    previous_enum = sa.Enum(*old_values, name='featuretoggle')
    new_enum = sa.Enum(*new_values, name='featuretoggle')

    temporary_enum = sa.Enum(*new_values, name='tmp_featuretoggle')
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE tmp_featuretoggle'
               ' USING name::text::tmp_featuretoggle')

    previous_enum.drop(op.get_bind(), checkfirst=False)

    new_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE featuretoggle'
               ' USING name::text::featuretoggle')

    temporary_enum.drop(op.get_bind(), checkfirst=False)


def downgrade():
    old_values = ('WEBAPP_SIGNUP', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE',
                  'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE', 'SEARCH_ALGOLIA', 'SEARCH_LEGACY',
                  'BENEFICIARIES_IMPORT', 'SYNCHRONIZE_ALGOLIA', 'SYNCHRONIZE_ALLOCINE',
                  'SYNCHRONIZE_BANK_INFORMATION', 'SYNCHRONIZE_LIBRAIRES', 'SYNCHRONIZE_TITELIVE',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS', 'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS', 'UPDATE_DISCOVERY_VIEW', 'UPDATE_BOOKING_USED',
                  'RECOMMENDATIONS_WITH_DISCOVERY_VIEW', 'RECOMMENDATIONS_WITH_DIGITAL_FIRST',
                  'RECOMMENDATIONS_WITH_GEOLOCATION', 'NEW_RIBS_UPLOAD', 'SAVE_SEEN_OFFERS', 'API_SIRENE_AVAILABLE',
                  'CLEAN_DISCOVERY_VIEW')

    new_values = ('WEBAPP_SIGNUP', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE',
                  'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE', 'SEARCH_ALGOLIA', 'SEARCH_LEGACY',
                  'BENEFICIARIES_IMPORT', 'SYNCHRONIZE_ALGOLIA', 'SYNCHRONIZE_ALLOCINE',
                  'SYNCHRONIZE_BANK_INFORMATION', 'SYNCHRONIZE_LIBRAIRES', 'SYNCHRONIZE_TITELIVE',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS', 'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS', 'UPDATE_DISCOVERY_VIEW', 'UPDATE_BOOKING_USED',
                  'RECOMMENDATIONS_WITH_DISCOVERY_VIEW', 'RECOMMENDATIONS_WITH_DIGITAL_FIRST',
                  'RECOMMENDATIONS_WITH_GEOLOCATION', 'NEW_RIBS_UPLOAD', 'SAVE_SEEN_OFFERS', 'BOOKINGS_V2',
                  'API_SIRENE_AVAILABLE', 'CLEAN_DISCOVERY_VIEW')

    previous_enum = sa.Enum(*old_values, name='featuretoggle')
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
                    VALUES ('%s', '%s', TRUE);
                    """ % (FeatureToggle.BOOKINGS_V2.name, FeatureToggle.BOOKINGS_V2.value))

    temporary_enum.drop(op.get_bind(), checkfirst=False)
