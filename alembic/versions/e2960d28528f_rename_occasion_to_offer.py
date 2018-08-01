"""Rename offer to stock and occasion to offer

Revision ID: e2960d28528f
Revises: 0e764b59ccbc
Create Date: 2018-08-01 06:52:54.926305

"""
from alembic import op

from models import Stock


# revision identifiers, used by Alembic.
revision = 'e2960d28528f'
down_revision = '0e764b59ccbc'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
      'BEGIN TRANSACTION;'
        'DROP TABLE IF EXISTS "stock";'  # automatically created by SQLAlchemy
        'ALTER TABLE "offer" RENAME TO "stock";'
        'ALTER SEQUENCE "offer_id_seq" RENAME TO "stock_id_seq";'
        'ALTER TABLE "stock" RENAME CONSTRAINT "offer_pkey" TO "stock_pkey";'
        'ALTER TABLE "stock" RENAME COLUMN "occasionId" TO "offerId";'
        'ALTER TABLE "stock" RENAME CONSTRAINT "offer_idAtProviders_key" TO "stock_idAtProviders_key";'
        'ALTER TABLE "stock" RENAME CONSTRAINT "offer_lastProviderId_fkey" TO "stock_lastProviderId_fkey";'
        'ALTER TABLE "stock" RENAME CONSTRAINT "offer_occasionId_fkey" TO "stock_offerId_fkey";'
        'ALTER TABLE "stock" RENAME CONSTRAINT "offer_eventOccurrenceId_fkey" TO "stock_eventOccurrenceId_fkey";'
        'ALTER TABLE "stock" RENAME CONSTRAINT "check_offer_has_event_occurrence_or_occasion" TO "check_offer_has_event_occurrence_or_offer";'
        'ALTER INDEX "ix_stock_occasionId" RENAME TO "ix_stock_offerId";'

        'ALTER TABLE "occasion" RENAME TO "offer";'
        'ALTER SEQUENCE "occasion_id_seq" RENAME TO "offer_id_seq";'
        'ALTER TABLE "offer" RENAME CONSTRAINT "occasion_pkey" TO "offer_pkey";'
        'ALTER TABLE "offer" RENAME CONSTRAINT "check_occasion_has_thing_xor_event" TO "check_offer_has_thing_xor_event";'
        'ALTER TABLE "offer" RENAME CONSTRAINT "occasion_eventId_fkey" TO "offer_eventId_fkey";'
        'ALTER TABLE "offer" RENAME CONSTRAINT "occasion_lastProviderId_fkey" TO "offer_lastProviderId_fkey";'
        'ALTER TABLE "offer" RENAME CONSTRAINT "occasion_venueId_fkey" TO "offer_venueId_fkey";'
        'ALTER TABLE "offer" RENAME CONSTRAINT "occasion_idAtProviders_key" TO "offer_idAtProviders_key";'
        'ALTER TABLE "offer" RENAME CONSTRAINT "occasion_thingId_fkey" TO "offer_thingId_fkey";'

        'ALTER INDEX "ix_booking_offerId" RENAME TO "ix_booking_stockId";'
        'ALTER INDEX "ix_event_occurrence_occasionId" RENAME TO "ix_event_occurrence_offerId";'
        'ALTER INDEX "ix_mediation_occasionId" RENAME TO "ix_mediation_offerId";'
        'ALTER INDEX "ix_occasion_venueId" RENAME TO "ix_offer_venueId";'
        'ALTER INDEX "ix_offer_available" RENAME TO "ix_stock_available";'
        'ALTER INDEX "ix_offer_eventOccurrenceId" RENAME TO "ix_stock_eventOccurrenceId";'
        'ALTER INDEX "ix_offer_occasionId" RENAME TO "ix_stock_occasionId";'

        'ALTER TABLE "booking" RENAME COLUMN "offerId" TO "stockId";'
        'ALTER TABLE "booking" RENAME CONSTRAINT "booking_offerId_fkey" TO "booking_stockId_fkey";'
        'ALTER TABLE "event_occurrence" RENAME COLUMN "occasionId" TO "offerId";'
        'ALTER TABLE "event_occurrence" RENAME CONSTRAINT "event_occurrence_occasionId_fkey" TO "event_occurrence_offerId_fkey";'
        'ALTER TABLE "mediation" RENAME COLUMN "occasionId" TO "offerId";'
        'ALTER TABLE "mediation" RENAME CONSTRAINT "mediation_occasionId_fkey" TO "mediation_offerId_fkey";'
        'ALTER TABLE "recommendation" RENAME COLUMN "occasionId" TO "offerId";'
        'ALTER TABLE "recommendation" RENAME CONSTRAINT "recommendation_occasionId_fkey" TO "recommendation_offerId_fkey";'
        'ALTER INDEX "ix_recommendation_occasionId" RENAME TO "ix_recommendation_offerId";'

        'DROP TRIGGER offer_update ON stock;'
        'DROP FUNCTION check_offer;'
        + Stock.trig_ddl + ';'
      'COMMIT;')


def downgrade():
    pass
