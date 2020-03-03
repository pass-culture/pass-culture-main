"""add_cron_feature_flipping

Revision ID: ba456c84727a
Revises: b8edbf51e278
Create Date: 2020-02-28 08:50:17.230781

"""
from enum import Enum

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'ba456c84727a'
down_revision = 'b8edbf51e278'
branch_labels = None
depends_on = None


class FeatureToggle(Enum):
    BENEFICIARIES_IMPORT = 'Permettre l''import des comptes jeunes depuis DMS'
    SYNCHRONIZE_ALGOLIA = 'Permettre la mise à jour des données pour la recherche via Algolia'
    SYNCHRONIZE_ALLOCINE = 'Permettre la synchronisation journalière avec Allociné'
    SYNCHRONIZE_BANK_INFORMATION = 'Permettre la synchronisation journalière avec DMS' \
                                   ' pour récupérer les informations bancaires des acteurs'
    SYNCHRONIZE_LIBRAIRES = 'Permettre la synchronisation journalière avec leslibraires.fr'
    SYNCHRONIZE_TITELIVE = 'Permettre la synchronisation journalière avec TiteLive / Epagine'
    SYNCHRONIZE_TITELIVE_PRODUCTS = 'Permettre l''import journalier du référentiel des livres'
    SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION = 'Permettre l''import journalier des résumés des livres'
    SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS = 'Permettre l''import journalier des couvertures de livres'
    UPDATE_DISCOVERY_VIEW = 'Permettre la mise à jour des données du carousel'
    UPDATE_BOOKING_USED = 'Permettre la validation automatique des contremarques 48h après la fin de l''évènement'


def upgrade():
    new_values = ('WEBAPP_SIGNUP', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE',
                  'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE', 'SEARCH_ALGOLIA', 'SEARCH_LEGACY',
                  'BENEFICIARIES_IMPORT', 'SYNCHRONIZE_ALGOLIA', 'SYNCHRONIZE_ALLOCINE',
                  'SYNCHRONIZE_BANK_INFORMATION', 'SYNCHRONIZE_LIBRAIRES', 'SYNCHRONIZE_TITELIVE',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS', 'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS', 'UPDATE_DISCOVERY_VIEW', 'UPDATE_BOOKING_USED')
    previous_values = ('WEBAPP_SIGNUP', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'DUO_OFFER', 'QR_CODE',
                       'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE', 'SEARCH_ALGOLIA', 'SEARCH_LEGACY')

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
    for feature in FeatureToggle:
        op.execute("""
                    INSERT INTO feature (name, description, "isActive")
                    VALUES ('%s', '%s', FALSE);
                    """ % (feature.name, feature.value))

    temporary_enum.drop(op.get_bind(), checkfirst=False)


def downgrade():
    new_values = ('WEBAPP_SIGNUP', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'DUO_OFFER', 'QR_CODE',
                  'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE', 'SEARCH_ALGOLIA', 'SEARCH_LEGACY')
    previous_values = ('WEBAPP_SIGNUP', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE',
                       'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE', 'SEARCH_ALGOLIA', 'SEARCH_LEGACY',
                       'BENEFICIARIES_IMPORT', 'SYNCHRONIZE_ALGOLIA', 'SYNCHRONIZE_ALLOCINE',
                       'SYNCHRONIZE_BANK_INFORMATION', 'SYNCHRONIZE_LIBRAIRES', 'SYNCHRONIZE_TITELIVE',
                       'SYNCHRONIZE_TITELIVE_PRODUCTS', 'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
                       'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS', 'UPDATE_DISCOVERY_VIEW', 'UPDATE_BOOKING_USED')

    previous_enum = sa.Enum(*previous_values, name='featuretoggle')
    new_enum = sa.Enum(*new_values, name='featuretoggle')
    temporary_enum = sa.Enum(*new_values, name='tmp_featuretoggle')

    op.execute("""
                DELETE FROM feature WHERE name IN ('SYNCHRONIZE_LIBRAIRES', 'SYNCHRONIZE_BANK_INFORMATION',
                 'BENEFICIARIES_IMPORT', 'SYNCHRONIZE_TITELIVE_PRODUCTS', 'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
                 'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS', 'SYNCHRONIZE_TITELIVE', 'SYNCHRONIZE_ALLOCINE',
                 'UPDATE_DISCOVERY_VIEW', 'UPDATE_BOOKING_USED', 'SYNCHRONIZE_ALGOLIA')
    """)
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE TMP_FEATURETOGGLE'
               ' USING name::TEXT::TMP_FEATURETOGGLE')
    previous_enum.drop(op.get_bind(), checkfirst=False)
    new_enum.create(op.get_bind(), checkfirst=False)

    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE FEATURETOGGLE'
               ' USING name::TEXT::FEATURETOGGLE')
    temporary_enum.drop(op.get_bind(), checkfirst=False)
