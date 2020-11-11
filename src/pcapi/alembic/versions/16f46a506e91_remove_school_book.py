"""remove_school_book

Revision ID: 16f46a506e91
Revises: 75beace17726
Create Date: 2019-09-05 14:06:50.618523

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "16f46a506e91"
down_revision = "2180c04babb0"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        DELETE FROM product
        WHERE "idAtProviders" IS NOT NULL
          AND "extraData"::jsonb ->> 'schoolbook' = 'true'
    """
    )


def downgrade():
    pass
