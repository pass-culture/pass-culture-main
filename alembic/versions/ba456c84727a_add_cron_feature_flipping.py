"""add_cron_feature_flipping

Revision ID: ba456c84727a
Revises: 771cab29d46e
Create Date: 2020-02-28 08:50:17.230781

"""
from enum import Enum

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'ba456c84727a'
down_revision = '771cab29d46e'
branch_labels = None
depends_on = None


class FeatureToggle(Enum):
    SYNCHRONIZE_BANK_INFORMATION = 'Permettre la synchronisation journalière avec DMS' \
                                   ' pour récupérer les informations bancaires des acteurs'
    BENEFICIARIES_IMPORT = 'Permettre l''import des comptes jeunes depuis DMS'
    SYNCHRONIZE_TITELIVE_PRODUCTS = 'Permettre l''import journalier du référentiel des livres'
    SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION = 'Permettre l''import journalier des résumés des livres'
    SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS = 'Permettre l''import journalier des couvertures de livres'
    SYNCHRONIZE_TITELIVE = 'Permettre la synchronisation journalière avec TiteLive / Epagine'
    SYNCHRONIZE_ALLOCINE = 'Permettre la synchronisation journalière avec Allociné'
    SYNCHRONIZE_LIBRAIRES = 'Permettre la synchronisation journalière avec leslibraires.fr'
    UPDATE_DISCOVERY_VIEW = 'Permettre la mise à jour des données du carousel'
    UPDATE_BOOKING_USED = 'Permettre la validation automatique des contremarques 48h après la fin de l''évènement'
    RESEND_EMAIL_IN_ERROR = 'Permettre de renvoyer les emails en erreur'
    SYNCHRONIZE_ALGOLIA = 'Permettre la mise à jour des données pour la recherche via Algolia'


def upgrade():
    new_values = ('WEBAPP_SIGNUP', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE',
                  'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE', 'SEARCH_ALGOLIA', 'SEARCH_LEGACY',
                  'SYNCHRONIZE_LIBRAIRES', 'SYNCHRONIZE_BANK_INFORMATION', 'BENEFICIARIES_IMPORT',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS', 'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS', 'SYNCHRONIZE_TITELIVE', 'SYNCHRONIZE_ALLOCINE',
                  'UPDATE_DISCOVERY_VIEW', 'UPDATE_BOOKING_USED', 'RESEND_EMAIL_IN_ERROR', 'SYNCHRONIZE_ALGOLIA')
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
                       'SYNCHRONIZE_LIBRAIRES', 'SYNCHRONIZE_BANK_INFORMATION', 'BENEFICIARIES_IMPORT',
                       'SYNCHRONIZE_TITELIVE_PRODUCTS', 'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
                       'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS', 'SYNCHRONIZE_TITELIVE', 'SYNCHRONIZE_ALLOCINE',
                       'UPDATE_DISCOVERY_VIEW', 'UPDATE_BOOKING_USED', 'RESEND_EMAIL_IN_ERROR', 'SYNCHRONIZE_ALGOLIA')

    previous_enum = sa.Enum(*previous_values, name='featuretoggle')
    new_enum = sa.Enum(*new_values, name='featuretoggle')
    temporary_enum = sa.Enum(*new_values, name='tmp_featuretoggle')

    op.execute("""
                DELETE FROM feature WHERE name IN ('SYNCHRONIZE_LIBRAIRES', 'SYNCHRONIZE_BANK_INFORMATION',
                 'BENEFICIARIES_IMPORT', 'SYNCHRONIZE_TITELIVE_PRODUCTS', 'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
                 'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS', 'SYNCHRONIZE_TITELIVE', 'SYNCHRONIZE_ALLOCINE',
                 'UPDATE_DISCOVERY_VIEW', 'UPDATE_BOOKING_USED', 'RESEND_EMAIL_IN_ERROR', 'SYNCHRONIZE_ALGOLIA')
    """)
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE TMP_FEATURETOGGLE'
               ' USING name::TEXT::TMP_FEATURETOGGLE')
    previous_enum.drop(op.get_bind(), checkfirst=False)
    new_enum.create(op.get_bind(), checkfirst=False)

    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE FEATURETOGGLE'
               ' USING name::TEXT::FEATURETOGGLE')
    temporary_enum.drop(op.get_bind(), checkfirst=False)
