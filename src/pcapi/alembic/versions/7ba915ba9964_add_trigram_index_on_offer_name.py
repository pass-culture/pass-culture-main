"""add_trigram_index_on_offer_name

Revision ID: 7ba915ba9964
Revises: 3aad2af23448
Create Date: 2020-11-23 15:18:40.967069

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "7ba915ba9964"
down_revision = "3aad2af23448"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")  # Close the automatically opened transaction so we can create/drop indexes "concurrently"
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_offer_fts_name";""")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    op.execute(
        """CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_offer_trgm_name" ON offer USING gin (name gin_trgm_ops);"""
    )


def downgrade():
    op.execute("COMMIT")  # Close the automatically opened transaction so we can create/drop indexes "concurrently"
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_offer_trgm_name";""")
    op.execute(
        """CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_offer_fts_name" ON offer USING gin (to_tsvector('french_unaccent'::regconfig, name::text));"""
    )
