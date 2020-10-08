"""modify_has_filled_cultural_survey_into_needs_to_fill_cultural_survey

Revision ID: ec50928d7331
Revises: 0df577e35e9f
Create Date: 2019-06-20 07:46:29.856135

"""
from alembic import op
from sqlalchemy.sql import expression


# revision identifiers, used by Alembic.
revision = 'ec50928d7331'
down_revision = '0df577e35e9f'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'user',
        'hasFilledCulturalSurvey',
        new_column_name='needsToFillCulturalSurvey',
        server_default=expression.true()
    )
    op.execute("""
        UPDATE "user"
        SET "needsToFillCulturalSurvey" = False
        """)



def downgrade():
    op.alter_column(
        'user',
        'needsToFillCulturalSurvey',
        new_column_name='hasFilledCulturalSurvey',
        server_default=expression.false()
    )
    op.execute("""
        UPDATE "user"
        SET "hasFilledCulturalSurvey" = True
        """)
