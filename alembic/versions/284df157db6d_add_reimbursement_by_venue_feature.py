"""add_reimbursement_by_venue_feature

Revision ID: 284df157db6d
Revises: 883df84383c1
Create Date: 2019-08-14 12:37:43.969998

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from models.feature import FeatureToggle

revision = '284df157db6d'
down_revision = '883df84383c1'
branch_labels = None
depends_on = None


previous_values = ('WEBAPP_SIGNUP', 'FAVORITE_OFFER')
new_values = ('WEBAPP_SIGNUP', 'FAVORITE_OFFER', 'REIMBURSEMENT_BY_VENUE')

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
        """ % (FeatureToggle.REIMBURSEMENT_BY_VENUE.name, FeatureToggle.REIMBURSEMENT_BY_VENUE.value))
    temporary_enum.drop(op.get_bind(), checkfirst=False)


def downgrade():
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE tmp_featuretoggle'
               ' USING name::text::tmp_featuretoggle')
    new_enum.drop(op.get_bind(), checkfirst=False)
    previous_enum.create(op.get_bind(), checkfirst=False)
    op.execute("DELETE FROM feature WHERE name = 'REIMBURSEMENT_BY_VENUE'")
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE featuretoggle'
               ' USING name::text::featuretoggle')
    temporary_enum.drop(op.get_bind(), checkfirst=False)
