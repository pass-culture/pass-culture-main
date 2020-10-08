"""add cultural survey id

Revision ID: de36871d256e
Revises: ec50928d7331
Create Date: 2019-06-20 07:56:06.672547

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = 'de36871d256e'
down_revision = 'ec50928d7331'
branch_labels = None
depends_on = None



def upgrade():
    op.add_column('user', sa.Column('culturalSurveyId', UUID(), nullable=True))


def downgrade():
    op.drop_column('user', 'culturalSurveyId')
