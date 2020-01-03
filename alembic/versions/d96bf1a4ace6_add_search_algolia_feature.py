"""add_search_algolia_feature

Revision ID: d96bf1a4ace6
Revises: 75f2ccf2be82
Create Date: 2020-01-03 13:24:37.563981

"""
import enum

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd96bf1a4ace6'
down_revision = '75f2ccf2be82'
branch_labels = None
depends_on = None


previous_values = ('WEBAPP_SIGNUP', 'FAVORITE_OFFER', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'DUO_OFFER', 'QR_CODE')
new_values = ('WEBAPP_SIGNUP', 'FAVORITE_OFFER', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'DUO_OFFER', 'QR_CODE', 'SEARCH_ALGOLIA')


class FeatureToggle(enum.Enum):
    WEBAPP_SIGNUP = 'Permettre aux bénéficiaires de créer un compte'
    FAVORITE_OFFER = 'Permettre aux bénéficiaires d''ajouter des offres en favoris'
    DEGRESSIVE_REIMBURSEMENT_RATE = 'Permettre le remboursement avec un barème dégressif par lieu'
    DUO_OFFER = 'Permettre la réservation d’une offre pour soi et un accompagnant'
    QR_CODE = 'Permettre la validation d''une contremarque via QR code'
    SEARCH_ALGOLIA = 'Permettre la recherche via Algolia'


previous_enum = sa.Enum(*previous_values, name='featuretoggle')
new_enum = sa.Enum(*new_values, name='featuretoggle')
temporary_enum = sa.Enum(*new_values, name='tmp_featuretoggle')


def upgrade():
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
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE tmp_featuretoggle'
               ' USING name::text::tmp_featuretoggle')
    new_enum.drop(op.get_bind(), checkfirst=False)
    previous_enum.create(op.get_bind(), checkfirst=False)
    op.execute("DELETE FROM feature WHERE name = 'SEARCH_ALGOLIA'")
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE featuretoggle'
               ' USING name::text::featuretoggle')
    temporary_enum.drop(op.get_bind(), checkfirst=False)
