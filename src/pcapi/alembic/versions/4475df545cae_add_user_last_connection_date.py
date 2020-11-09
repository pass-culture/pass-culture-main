"""add_user_last_connection_date

Revision ID: 4475df545cae
Revises: e52827be0601
Create Date: 2020-08-12 09:13:37.522121

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4475df545cae'
down_revision = 'e52827be0601'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('lastConnectionDate', sa.DateTime(), nullable=True))
    op.execute('UPDATE "user" SET "lastConnectionDate" = subquery."culturalSurveyFilledDate" '
               'FROM (SELECT id, "culturalSurveyFilledDate" FROM "user") AS subquery '
               'WHERE "user".id = subquery.id')


def downgrade():
    op.drop_column('user', 'lastConnectionDate')
