"""Rename occurence to occurrence

Revision ID: 0e764b59ccbc
Revises: 7ce5154d87e2
Create Date: 2018-07-31 08:07:39.614788

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '0e764b59ccbc'
down_revision = '7ce5154d87e2'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
      'BEGIN TRANSACTION;'
        'DROP TABLE IF EXISTS "event_occurrence" CASCADE;'  # automatically created by SQLAlchemy
        'ALTER TABLE "event_occurence" RENAME TO "event_occurrence";'
        'ALTER SEQUENCE "event_occurence_id_seq" RENAME TO "event_occurrence_id_seq";'
        'ALTER TABLE "offer" RENAME COLUMN "eventOccurenceId" TO "eventOccurrenceId";'
        'ALTER TABLE "recommendation" RENAME COLUMN "inviteforEventOccurenceId" TO "inviteforEventOccurrenceId";'

        'ALTER INDEX "ix_event_occurence_beginningDatetime" RENAME TO "ix_event_occurrence_beginningDatetime";'
        'ALTER INDEX "ix_event_occurence_occasionId" RENAME TO "ix_event_occurrence_occasionId";'
        'ALTER INDEX "ix_offer_eventOccurenceId" RENAME TO "ix_offer_eventOccurrenceId";'

        'ALTER TABLE event_occurrence RENAME CONSTRAINT "event_occurence_idAtProviders_key"   TO "event_occurrence_idAtProviders_key"  ;'
        'ALTER TABLE event_occurrence RENAME CONSTRAINT "event_occurence_pkey"                TO "event_occurrence_pkey"               ;'
        'ALTER TABLE event_occurrence RENAME CONSTRAINT "event_occurence_lastProviderId_fkey" TO "event_occurrence_lastProviderId_fkey";'
        'ALTER TABLE event_occurrence RENAME CONSTRAINT "event_occurence_occasionId_fkey"     TO "event_occurrence_occasionId_fkey"    ;'

        'ALTER TABLE offer DROP CONSTRAINT IF EXISTS "check_offer_has_event_occurence_or_occasion";'
        'ALTER TABLE offer ADD CONSTRAINT "check_offer_has_event_occurrence_or_occasion" CHECK ((("eventOccurrenceId" IS NOT NULL) OR ("occasionId" IS NOT NULL)));'

        'ALTER TABLE offer RENAME CONSTRAINT "offer_eventOccurenceId_fkey" TO "offer_eventOccurrenceId_fkey";'
        'ALTER TABLE recommendation RENAME CONSTRAINT "recommendation_inviteforEventOccurenceId_fkey" TO "recommendation_inviteforEventOccurrenceId_fkey";'
        + """
        CREATE OR REPLACE FUNCTION check_offer()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NOT NEW.available IS NULL AND
            ((SELECT COUNT(*) FROM booking WHERE "offerId"=NEW.id) > NEW.available) THEN
                RAISE EXCEPTION 'available_too_low'
                USING HINT = 'offer.available cannot be lower than number of bookings';
            END IF;
            
            IF NOT NEW."bookingLimitDatetime" IS NULL AND
            (NEW."bookingLimitDatetime" > (SELECT "beginningDatetime" FROM event_occurrence WHERE id=NEW."eventOccurrenceId")) THEN
            
            RAISE EXCEPTION 'bookingLimitDatetime_too_late'
            USING HINT = 'offer.bookingLimitDatetime after event_occurrence.beginningDatetime';
            END IF;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        DROP TRIGGER IF EXISTS offer_update ON offer;
        CREATE CONSTRAINT TRIGGER offer_update AFTER INSERT OR UPDATE 
        ON offer 
        FOR EACH ROW EXECUTE PROCEDURE check_offer()
      """ + ';'
      'COMMIT;'
    )
    pass


def downgrade():
    pass
