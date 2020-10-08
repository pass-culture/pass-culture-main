"""add_cultural_survey_filled_date_on_user

Revision ID: 21ef2b9af5e6
Revises: 22402024bce9
Create Date: 2019-12-06 09:21:40.650337

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '21ef2b9af5e6'
down_revision = '22402024bce9'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('culturalSurveyFilledDate', sa.DateTime, nullable=True))


def downgrade():
    op.drop_column('user', 'culturalSurveyFilledDate')
