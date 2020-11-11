""" correct stock_update trigger

Revision ID: 802c89135fd7
Revises: ec8d3f04eba3
Create Date: 2019-03-26 14:42:25.756908

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "802c89135fd7"
down_revision = "ec8d3f04eba3"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
    CREATE OR REPLACE FUNCTION check_stock()
    RETURNS TRIGGER AS $$
    BEGIN
      IF 
       NOT NEW.available IS NULL 
       AND
        (
         (
          SELECT SUM(booking.quantity) 
          FROM booking 
          WHERE "stockId"=NEW.id
          AND NOT booking."isCancelled"
         ) > NEW.available
        ) 
      THEN
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
    """
    )


def downgrade():
    op.execute(
        """
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
            """
    )
