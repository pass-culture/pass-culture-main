from sqlalchemy import DDL, event

from models.booking import Booking

trig_ddl = DDL("""
    CREATE OR REPLACE FUNCTION check_booking()
    RETURNS TRIGGER AS $$
    BEGIN
      IF EXISTS (SELECT "available" FROM offer WHERE id=NEW."offerId" AND "available" IS NOT NULL)
         AND ((SELECT "available" FROM offer WHERE id=NEW."offerId")
              < (SELECT COUNT(*) FROM booking WHERE "offerId"=NEW."offerId")) THEN
          RAISE EXCEPTION 'Offer has too many bookings'
                USING HINT = 'Number of bookings cannot exceed "offer.available"';
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE CONSTRAINT TRIGGER booking_update AFTER INSERT OR UPDATE
    ON booking
    FOR EACH ROW EXECUTE PROCEDURE check_booking()
    """)
event.listen(Booking.__table__,
             'after_create',
             trig_ddl)
