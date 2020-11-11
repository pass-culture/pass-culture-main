"""Remove fulltext search on author artist and description for offer

Revision ID: a96683bbf3be
Revises: 979af719f2f7
Create Date: 2020-09-21 15:40:34.289352

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "a96683bbf3be"
down_revision = "979af719f2f7"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")  # Close the automatically opened transaction so we can create/drop indexes "concurrently"
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_offer_fts_author";""")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_offer_fts_byArtist";""")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_offer_fts_description";""")
    pass


def downgrade():
    op.execute("COMMIT")  # Close the automatically opened transaction so we can create/drop indexes "concurrently"
    op.execute(
        """CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_offer_fts_author" ON offer USING gin (to_tsvector('french_unaccent'::regconfig, ("extraData" -> 'author'::text)::text));"""
    )
    op.execute(
        """CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_offer_fts_byArtist" ON offer USING gin (to_tsvector('french_unaccent'::regconfig, ("extraData" -> 'byArtist'::text)::text));"""
    )
    op.execute(
        """CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_offer_fts_description" ON offer USING gin (to_tsvector('french_unaccent'::regconfig, description));"""
    )
    pass
