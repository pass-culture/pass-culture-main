""" Remove table event occurrence

Revision ID: 989e483edf93
Revises: 802c89135fd7
Create Date: 2019-03-14 13:23:34.641583

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '989e483edf93'
down_revision = '802c89135fd7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('stock', sa.Column('beginningDatetime', sa.DateTime, nullable=True, index=True))
    op.add_column('stock', sa.Column('endDatetime', sa.DateTime, nullable=True))
    op.drop_constraint('check_stock_has_event_occurrence_xor_offer', 'stock')
    op.execute("""
    UPDATE stock s SET
        "beginningDatetime" = (SELECT "beginningDatetime" FROM event_occurrence eo WHERE s."eventOccurrenceId" = eo.id),
        "endDatetime" = (SELECT "endDatetime" FROM event_occurrence eo WHERE s."eventOccurrenceId" = eo.id),
        "offerId" = (SELECT "offerId" FROM event_occurrence eo WHERE s."eventOccurrenceId" = eo.id),
        "isSoftDeleted" = (SELECT eo."isSoftDeleted" FROM event_occurrence eo WHERE s."eventOccurrenceId" = eo.id) OR s."isSoftDeleted"
    WHERE s."offerId" IS NULL;
    """)
    op.drop_column('stock', 'eventOccurrenceId')
    op.drop_column('recommendation', 'inviteforEventOccurrenceId')
    op.alter_column('stock', 'offerId', existing_type=sa.BigInteger, nullable=False)
    op.drop_table('event_occurrence')

    op.execute("""
       CREATE OR REPLACE FUNCTION check_stock()
       RETURNS TRIGGER AS $$
       BEGIN
         IF NOT NEW.available IS NULL AND
         ((SELECT COUNT(*) FROM booking WHERE "stockId"=NEW.id) > NEW.available) THEN
           RAISE EXCEPTION 'available_too_low'
                 USING HINT = 'stock.available cannot be lower than number of bookings';
         END IF;

         IF NOT NEW."bookingLimitDatetime" IS NULL AND
            NOT NEW."beginningDatetime" IS NULL AND
            NEW."bookingLimitDatetime" > NEW."beginningDatetime" THEN

         RAISE EXCEPTION 'bookingLimitDatetime_too_late'
         USING HINT = 'bookingLimitDatetime after beginningDatetime';
         END IF;

         RETURN NEW;
       END;
       $$ LANGUAGE plpgsql;

       DROP TRIGGER IF EXISTS stock_update ON stock;
       CREATE CONSTRAINT TRIGGER stock_update AFTER INSERT OR UPDATE
       ON stock
       FOR EACH ROW EXECUTE PROCEDURE check_stock()
    """)


def downgrade():
    op.execute("""
    CREATE TABLE event_occurrence (
        "isSoftDeleted" boolean NOT NULL,
        "idAtProviders" character varying(70),
        "dateModifiedAtLastProvider" timestamp without time zone,
        id bigint NOT NULL,
        type eventtype,
        "offerId" bigint NOT NULL,
        "beginningDatetime" timestamp without time zone NOT NULL,
        "endDatetime" timestamp without time zone NOT NULL,
        accessibility bytea,
        "lastProviderId" bigint,
        CONSTRAINT check_end_datetime_is_after_beginning_datetime CHECK (("endDatetime" > "beginningDatetime")),
        CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL)))
    );
    
    INSERT INTO
        event_occurrence ("id", "beginningDatetime", "endDatetime", "offerId", "idAtProviders", "lastProviderId", "isSoftDeleted") 
    SELECT
        id, "beginningDatetime", "endDatetime", "offerId", "idAtProviders", "lastProviderId", "isSoftDeleted"
    FROM
        stock
    WHERE "beginningDatetime" IS NOT NULL;
    
    CREATE SEQUENCE event_occurrence_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

    ALTER TABLE ONLY event_occurrence ALTER COLUMN id SET DEFAULT nextval('event_occurrence_id_seq'::regclass);
    """)

    op.add_column('recommendation', sa.Column('inviteforEventOccurrenceId', sa.BigInteger, nullable=True))
    op.add_column('stock', sa.Column('eventOccurrenceId', sa.BigInteger, nullable=True))
    op.alter_column('stock', 'offerId', existing_type=sa.BigInteger, nullable=True)

    op.execute("""
        UPDATE stock SET "eventOccurrenceId" = id, "offerId" = NULL WHERE "beginningDatetime" IS NOT NULL;
        ALTER TABLE stock
        ADD CONSTRAINT check_stock_has_event_occurrence_xor_offer
        CHECK (
            ((("eventOccurrenceId" IS NOT NULL) AND ("offerId" IS NULL))
            OR (("eventOccurrenceId" IS NULL) AND ("offerId" IS NOT NULL)))
        );
        
        SELECT pg_catalog.setval('event_occurrence_id_seq', (SELECT MAX(id) FROM event_occurrence), true);
    """)

    op.drop_column('stock', 'beginningDatetime')
    op.drop_column('stock', 'endDatetime')
    op.execute("""
        CREATE OR REPLACE FUNCTION check_stock()
        RETURNS TRIGGER AS $$
        BEGIN
          IF NOT NEW.available IS NULL AND
          ((SELECT COUNT(*) FROM booking WHERE "stockId"=NEW.id) > NEW.available) THEN
            RAISE EXCEPTION 'available_too_low'
                  USING HINT = 'stock.available cannot be lower than number of bookings';
          END IF;

          IF NOT NEW."bookingLimitDatetime" IS NULL AND
          (NEW."bookingLimitDatetime" > (SELECT "beginningDatetime" FROM event_occurrence WHERE id=NEW."eventOccurrenceId")) THEN

          RAISE EXCEPTION 'bookingLimitDatetime_too_late'
          USING HINT = 'stock.bookingLimitDatetime after event_occurrence.beginningDatetime';
          END IF;

          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS stock_update ON stock;
        CREATE CONSTRAINT TRIGGER stock_update AFTER INSERT OR UPDATE
        ON stock
        FOR EACH ROW EXECUTE PROCEDURE check_stock()
    """)

