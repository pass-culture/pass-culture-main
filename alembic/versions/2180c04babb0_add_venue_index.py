"""add index on city for venue

Revision ID: 2180c04babb0
Revises: 75beace17726
Create Date: 2019-09-06 12:22:05.931182

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '2180c04babb0'
down_revision = '75beace17726'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
            CREATE INDEX IF NOT EXISTS "idx_venue_fts_city" ON venue USING gin (to_tsvector('french_unaccent'::regconfig, "city"::text));
        """
    )


def downgrade():
    op.execute(
        """
          DROP INDEX "idx_venue_fts_city";
        """
    )
