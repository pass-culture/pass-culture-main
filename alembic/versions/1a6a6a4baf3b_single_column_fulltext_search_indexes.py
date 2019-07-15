"""Separate indexes for full text search

Revision ID: 1a6a6a4baf3b
Revises: 926f236ee66f
Create Date: 2019-07-11 12:39:08.375319

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '1a6a6a4baf3b'
down_revision = '926f236ee66f'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")  # Close the automatically opened transaction so we can create/drop indexes "concurrently"
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_event_fts";""")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_offer_fts";""")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_offerer_fts";""")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_venue_fts";""")
    op.execute("""CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_offer_fts_author" ON offer USING gin (to_tsvector('french_unaccent'::regconfig, ("extraData" -> 'author'::text)::text));""")
    op.execute("""CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_offer_fts_byArtist" ON offer USING gin (to_tsvector('french_unaccent'::regconfig, ("extraData" -> 'byArtist'::text)::text));""")
    op.execute("""CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_offer_fts_description" ON offer USING gin (to_tsvector('french_unaccent'::regconfig, description));""")
    op.execute("""CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_offer_fts_name" ON offer USING gin (to_tsvector('french_unaccent'::regconfig, name::text));""")
    op.execute("""CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_product_fts_author" ON product USING gin (to_tsvector('french_unaccent'::regconfig, ("extraData" -> 'author'::text)::text));""")
    op.execute("""CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_product_fts_byArtist" ON product USING gin (to_tsvector('french_unaccent'::regconfig, ("extraData" -> 'byArtist'::text)::text));""")
    op.execute("""CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_product_fts_description" ON product USING gin (to_tsvector('french_unaccent'::regconfig, description));""")
    op.execute("""CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_product_fts_name" ON product USING gin (to_tsvector('french_unaccent'::regconfig, name::text));""")
    op.execute("""CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_venue_fts_address" ON venue USING gin (to_tsvector('french_unaccent'::regconfig, address::text));""")
    op.execute("""CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_venue_fts_name" ON venue USING gin (to_tsvector('french_unaccent'::regconfig, name::text));""")
    op.execute("""CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_venue_fts_publicName" ON venue USING gin (to_tsvector('french_unaccent'::regconfig, "publicName"::text));""")
    op.execute("""CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_venue_fts_siret" ON venue USING gin (to_tsvector('french_unaccent'::regconfig, siret::text));""")
    op.execute("""CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_offerer_fts_address" ON offerer USING gin (to_tsvector('french_unaccent'::regconfig, address::text));""")
    op.execute("""CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_offerer_fts_name" ON offerer USING gin (to_tsvector('french_unaccent'::regconfig, name::text));""")
    op.execute("""CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_offerer_fts_siret" ON offerer USING gin (to_tsvector('french_unaccent'::regconfig, siren::text));""")


def downgrade():
    op.execute("COMMIT")  # Close the automatically opened transaction so we can create/drop indexes "concurrently"
    op.execute("""CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_event_fts" ON product USING gin (to_tsvector('french_unaccent'::regconfig, (COALESCE(name, ''::character varying)::text || ' '::text) || COALESCE(description, ''::text)));""")
    op.execute("""CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_offer_fts" ON offer USING gin (to_tsvector('french_unaccent'::regconfig, (((((COALESCE(name, ''::character varying)::text || ' '::text) || COALESCE(("extraData" -> 'author'::text)::text, ''::text)) || ' '::text) || COALESCE(("extraData" -> 'byArtist'::text)::text, ''::text)) || ' '::text) || COALESCE(description, ''::text)));""")
    op.execute("""CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_offerer_fts" ON offerer USING gin (to_tsvector('french_unaccent'::regconfig, (((COALESCE(name, ''::character varying)::text || ' '::text) || COALESCE(address, ''::character varying)::text) || ' '::text) || COALESCE(siren, ''::character varying)::text));""")
    op.execute("""CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_venue_fts" ON venue USING gin (to_tsvector('french_unaccent'::regconfig, (((COALESCE(name, ''::character varying)::text || ' '::text) || COALESCE(address, ''::character varying)::text) || ' '::text) || COALESCE(siret, ''::character varying)::text));""")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_offer_fts_author";""")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_offer_fts_byArtist";""")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_offer_fts_description";""")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_offer_fts_name";""")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_product_fts_author";""")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_product_fts_byArtist";""")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_product_fts_description";""")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_product_fts_name";""")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_venue_fts_address";""")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_venue_fts_name";""")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_venue_fts_publicName";""")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_venue_fts_siret";""")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_offerer_fts_address";""")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_offerer_fts_name";""")
    op.execute("""DROP INDEX CONCURRENTLY IF EXISTS "idx_offerer_fts_siret";""")
