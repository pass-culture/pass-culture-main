""" check stock without cancelled bookings

Revision ID: 3013952a110c
Revises: f9361bb484a1
Create Date: 2019-05-06 14:51:03.574377

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '3013952a110c'
down_revision = 'f9361bb484a1'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
           CREATE OR REPLACE FUNCTION check_stock()
           RETURNS TRIGGER AS $$
           BEGIN
            IF NOT NEW.available IS NULL AND
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
