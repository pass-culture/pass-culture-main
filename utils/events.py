""" events """
from sqlalchemy import DDL, event

from models.booking import Booking
from models.offer import Offer

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



@event.listens_for(Offer, 'before_insert')
def page_defaults(mapper, configuration, target):
    # `bookingLimitDatetime` defaults to midnight before `beginningDatetime`
    # for eventOccurences
    if target.eventOccurenceId and not target.bookingLimitDatetime:
        eventOccurence = target.eventOccurence
        if eventOccurence is None:
            eventOccurence = EventOccurence\
                                      .query\
                                      .filter_by(id=target.eventOccurenceId)\
                                      .first_or_404()
        target.bookingLimitDatetime = eventOccurence.beginningDatetime\
                                                    .replace(hour=23)\
                                                    .replace(minute=59) - timedelta(days=3)

trig_ddl = DDL("""
    CREATE OR REPLACE FUNCTION check_offer()
    RETURNS TRIGGER AS $$
    BEGIN
      IF NOT NEW.available IS NULL AND
      ((SELECT COUNT(*) FROM booking WHERE "offerId"=NEW.id) > NEW.available) THEN
        RAISE EXCEPTION 'available_too_low'
              USING HINT = 'offer.available cannot be lower than number of bookings';
      END IF;

      IF NOT NEW."bookingLimitDatetime" IS NULL AND
      (NEW."bookingLimitDatetime" > (SELECT "beginningDatetime" FROM event_occurence WHERE id=NEW."eventOccurenceId")) THEN

      RAISE EXCEPTION 'bookingLimitDatetime_too_late'
      USING HINT = 'offer.bookingLimitDatetime after event_occurence.beginningDatetime';
      END IF;

      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE CONSTRAINT TRIGGER offer_update AFTER INSERT OR UPDATE
    ON offer
    FOR EACH ROW EXECUTE PROCEDURE check_offer()
    """)
event.listen(Offer.__table__,
             'after_create',
             trig_ddl)
