"""mark all user as typeform validated

Revision ID: 67307cd6ee1b
:Create Date: 2019-06-07 08:59:33.971272

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '67307cd6ee1b'
down_revision = 'a89e0481fad6'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        UPDATE "user"
        SET "hasFilledCulturalSurvey" = True
        """)
    pass


def downgrade():
    op.execute("""
            UPDATE "user"
            SET "hasFilledCulturalSurvey" = False
            """)
    pass
