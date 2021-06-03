"""add_index_for_last_validation_date

Revision ID: 77d29ab6c382
Revises: 3605366e5ded
Create Date: 2021-05-27 08:12:41.256430

"""
from alembic import op

from pcapi import settings


# revision identifiers, used by Alembic.
revision = "77d29ab6c382"
down_revision = "3605366e5ded"
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
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_offer_lastValidationDate" ON offer ("lastValidationDate")
        """
    )
    op.execute(
        f"""
        SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
        """
    )


def downgrade():
    op.drop_index(op.f("ix_offer_lastValidationDate"), table_name="offer")
