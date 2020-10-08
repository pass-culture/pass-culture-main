"""Add has filled cultural survey to user

Revision ID: ebb2366cbf96
Revises: 09857d7d7492
Create Date: 2019-06-04 12:19:06.468967

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import expression

# revision identifiers, used by Alembic.
revision = 'ebb2366cbf96'
down_revision = '09857d7d7492'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('hasFilledCulturalSurvey', sa.BOOLEAN, server_default=expression.false()))


def downgrade():
    op.drop_column('user', 'hasFilledCulturalSurvey')
