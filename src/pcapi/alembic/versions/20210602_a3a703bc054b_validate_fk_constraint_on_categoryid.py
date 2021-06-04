"""validate FK constraint on categoryId

Revision ID: a3a703bc054b
Revises: 239aff25d73d
Create Date: 2021-06-02 15:39:58.777824

"""
from alembic import op

from pcapi import settings


# revision identifiers, used by Alembic.
revision = "a3a703bc054b"
down_revision = "239aff25d73d"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.execute(
        """
        SET SESSION statement_timeout = '300s'
        """
    )
    op.execute(
        """
        ALTER TABLE offer VALIDATE CONSTRAINT "offer_subcategoryId_fkey"
        """
    )
    op.execute(
        f"""
        SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
        """
    )


def downgrade():
    pass
