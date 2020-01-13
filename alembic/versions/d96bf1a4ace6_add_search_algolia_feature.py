"""add_search_algolia_feature

Revision ID: d96bf1a4ace6
Revises: 8f2c1fd24cad
Create Date: 2020-01-03 13:24:37.563981

"""
from alembic import op
import enum
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd96bf1a4ace6'
down_revision = '8f2c1fd24cad'
branch_labels = None
depends_on = None


class FeatureToggle(enum.Enum):
    SEARCH_ALGOLIA = 'Permettre la recherche via Algolia'


def upgrade():
    new_values = ('WEBAPP_SIGNUP',
                  'DEGRESSIVE_REIMBURSEMENT_RATE',
                  'QR_CODE',
                  'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE',
                  'SEARCH_ALGOLIA')
    previous_values = ('WEBAPP_SIGNUP',
                       'DEGRESSIVE_REIMBURSEMENT_RATE',
                       'QR_CODE',
                       'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE')

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
        """ % (FeatureToggle.SEARCH_ALGOLIA.name, FeatureToggle.SEARCH_ALGOLIA.value))
    temporary_enum.drop(op.get_bind(), checkfirst=False)


def downgrade():
    new_values = ('WEBAPP_SIGNUP',
                  'DEGRESSIVE_REIMBURSEMENT_RATE',
                  'QR_CODE',
                  'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE')
    previous_values = ('WEBAPP_SIGNUP',
                       'DEGRESSIVE_REIMBURSEMENT_RATE',
                       'QR_CODE',
                       'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE',
                       'SEARCH_ALGOLIA')

    previous_enum = sa.Enum(*previous_values, name='featuretoggle')
    new_enum = sa.Enum(*new_values, name='featuretoggle')
    temporary_enum = sa.Enum(*new_values, name='tmp_featuretoggle')

    op.execute("DELETE FROM feature WHERE name = 'SEARCH_ALGOLIA'")
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE tmp_featuretoggle'
               ' USING name::text::tmp_featuretoggle')
    previous_enum.drop(op.get_bind(), checkfirst=False)
    new_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE featuretoggle'
               ' USING name::text::featuretoggle')
    temporary_enum.drop(op.get_bind(), checkfirst=False)
