"""add_favorite_feature

Revision ID: 37ba62c7fdb3
Revises: 926f236ee66f
Create Date: 2019-07-09 09:47:32.341098

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import expression

# revision identifiers, used by Alembic.
from models.feature import FeatureToggle

revision = '37ba62c7fdb3'
down_revision = '926f236ee66f'
branch_labels = None
depends_on = None

previous_values = ('WEBAPP_SIGNUP',)
new_values = ('WEBAPP_SIGNUP', 'FAVORITE_OFFER')

previous_enum = sa.Enum(*previous_values, name='featuretoggle')
new_enum = sa.Enum(*new_values, name='featuretoggle')
temporary_enum = sa.Enum(*new_values, name='tmp_featuretoggle')


def upgrade():
    op.drop_column('recommendation', 'isFavorite')

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
        """ % (FeatureToggle.FAVORITE_OFFER.name, FeatureToggle.FAVORITE_OFFER.value))
    temporary_enum.drop(op.get_bind(), checkfirst=False)

    op.create_table(
        'favorite',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('userId', sa.BigInteger, nullable=False),
        sa.Column('offerId', sa.BigInteger, nullable=False),
        sa.Column('mediationId', sa.BigInteger, nullable=True)
    )


def downgrade():
    op.drop_table('favorite')

    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE tmp_featuretoggle'
               ' USING name::text::tmp_featuretoggle')
    new_enum.drop(op.get_bind(), checkfirst=False)
    previous_enum.create(op.get_bind(), checkfirst=False)
    op.execute("DELETE FROM feature WHERE name = 'FAVORITE_OFFER'")
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE featuretoggle'
               ' USING name::text::featuretoggle')
    temporary_enum.drop(op.get_bind(), checkfirst=False)

    op.add_column('recommendation',
                  sa.Column('isFavorite', sa.Boolean, nullable=False, server_default=expression.false()))
