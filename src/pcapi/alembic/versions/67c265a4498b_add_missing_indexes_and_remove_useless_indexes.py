"""Add missing indexes and remove useless indexes

Revision ID: 67c265a4498b
Revises: 52400a8d7e49
Create Date: 2019-11-07 08:36:01.261394

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '67c265a4498b'
down_revision = '52400a8d7e49'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        '''
        DROP INDEX IF EXISTS "idx_beneficiary_import_status_authorId";
        DROP INDEX IF EXISTS "idx_offer_criterion_criterionId";
        DROP INDEX IF EXISTS "ix_payment_transactionId";
        DROP INDEX IF EXISTS "idx_product_fts_byArtist";
        DROP INDEX IF EXISTS "idx_product_fts_name";
        DROP INDEX IF EXISTS "ix_product_type";
        DROP INDEX IF EXISTS "idx_product_fts_description";
        DROP INDEX IF EXISTS "idx_product_fts_author";
        DROP INDEX IF EXISTS "ix_recommendation_dateRead";
        DROP INDEX IF EXISTS "ix_stock_available";
        DROP INDEX IF EXISTS "ix_venue_departementCode";
        DROP INDEX IF EXISTS "ix_venue_provider_venueId";

        CREATE INDEX IF NOT EXISTS "idx_provider_name" ON provider ("name");
        CREATE INDEX IF NOT EXISTS "idx_venue_provider_providerId" ON venue_provider ("providerId");
        '''
    )


def downgrade():
    op.execute(
        '''
        CREATE INDEX IF NOT EXISTS "idx_beneficiary_import_status_authorId" ON beneficiary_import_status ("authorId");
        CREATE INDEX IF NOT EXISTS "idx_offer_criterion_criterionId" ON offer_criterion ("criterionId");
        CREATE INDEX IF NOT EXISTS "ix_payment_transactionId" ON payment ("paymentMessageId");
        CREATE INDEX IF NOT EXISTS "ix_product_type" ON product ("type");
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_product_fts_author" ON product USING gin (to_tsvector('french_unaccent'::regconfig, ("extraData" -> 'author'::text)::text));
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_product_fts_byArtist" ON product USING gin (to_tsvector('french_unaccent'::regconfig, ("extraData" -> 'byArtist'::text)::text));
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_product_fts_description" ON product USING gin (to_tsvector('french_unaccent'::regconfig, description));
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_product_fts_name" ON product USING gin (to_tsvector('french_unaccent'::regconfig, name::text));
        CREATE INDEX IF NOT EXISTS "ix_recommendation_dateRead" ON recommendation ("dateRead");
        CREATE INDEX IF NOT EXISTS "ix_stock_available" ON stock ("available");
        CREATE INDEX IF NOT EXISTS "ix_venue_departementCode" ON venue ("departementCode");
        CREATE INDEX IF NOT EXISTS "ix_venue_provider_venueId" ON venue_provider ("venueId");

        DROP INDEX IF EXISTS "idx_provider_name";
        DROP INDEX IF EXISTS "idx_venue_provider_providerId";
        '''
    )
