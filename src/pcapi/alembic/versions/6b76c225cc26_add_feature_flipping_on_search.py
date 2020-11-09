"""add_feature_flipping_on_search

Revision ID: 6b76c225cc26
Revises: d96bf1a4ace6
Create Date: 2020-01-14 10:08:12.434888

"""
import enum

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b76c225cc26'
down_revision = 'd96bf1a4ace6'
branch_labels = None
depends_on = None


class FeatureToggle(enum.Enum):
    SEARCH_LEGACY = "Permettre la recherche classique"


def upgrade():
    new_values = ('WEBAPP_SIGNUP',
                  'DEGRESSIVE_REIMBURSEMENT_RATE',
                  'QR_CODE',
                  'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE',
                  'SEARCH_ALGOLIA',
                  'SEARCH_LEGACY')
    previous_values = ('WEBAPP_SIGNUP',
                       'DEGRESSIVE_REIMBURSEMENT_RATE',
                       'QR_CODE',
                       'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE',
                       'SEARCH_ALGOLIA')

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


def downgrade():
    new_values = ('WEBAPP_SIGNUP',
                  'DEGRESSIVE_REIMBURSEMENT_RATE',
                  'QR_CODE',
                  'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE',
                  'SEARCH_ALGOLIA')
    previous_values = ('WEBAPP_SIGNUP',
                       'DEGRESSIVE_REIMBURSEMENT_RATE',
                       'QR_CODE',
                       'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE',
                       'SEARCH_ALGOLIA',
                       'SEARCH_LEGACY')

    previous_enum = sa.Enum(*previous_values, name='featuretoggle')
    new_enum = sa.Enum(*new_values, name='featuretoggle')
    temporary_enum = sa.Enum(*new_values, name='tmp_featuretoggle')

    op.execute("DELETE FROM feature WHERE name = 'SEARCH_LEGACY'")
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE tmp_featuretoggle'
               ' USING name::text::tmp_featuretoggle')
    previous_enum.drop(op.get_bind(), checkfirst=False)
    new_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE featuretoggle'
               ' USING name::text::featuretoggle')
    temporary_enum.drop(op.get_bind(), checkfirst=False)
