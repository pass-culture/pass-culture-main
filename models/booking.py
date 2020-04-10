from datetime import datetime, timedelta

from sqlalchemy import BigInteger, \
    Boolean, \
    Column, \
    DateTime, \
    DDL, \
    event, \
    ForeignKey, \
    Integer, \
    String, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from models.db import Model
from models.pc_object import PcObject
from models.versioned_mixin import VersionedMixin
from utils.human_ids import humanize


class Booking(PcObject, Model, VersionedMixin):
    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    dateCreated = Column(DateTime,
                         nullable=False,
                         default=datetime.utcnow)

    dateUsed = Column(DateTime,
                      nullable=True)

    recommendationId = Column(BigInteger,
                              ForeignKey("recommendation.id"),
                              index=True)

    recommendation = relationship('Recommendation',
                                  foreign_keys=[recommendationId],
                                  backref='bookings')

    stockId = Column(BigInteger,
                     ForeignKey("stock.id"),
                     index=True,
                     nullable=False)

    stock = relationship('Stock',
                         foreign_keys=[stockId],
                         backref='bookings')

    quantity = Column(Integer,
                      nullable=False,
                      default=1)

    token = Column(String(6),
                   unique=True,
                   nullable=False)

    userId = Column(BigInteger,
                    ForeignKey('user.id'),
                    index=True,
                    nullable=False)

    user = relationship('User',
                        foreign_keys=[userId],
                        backref='userBookings')

    amount = Column(Numeric(10, 2),
                    nullable=False)

    isCancelled = Column(Boolean,
                         nullable=False,
                         server_default=expression.false(),
                         default=False)

    cancellationDate = Column(DateTime, nullable=True)

    isUsed = Column(Boolean,
                    nullable=False,
                    default=False)

    @property
    def value(self):
        return self.amount * self.quantity

    @property
    def completedUrl(self):
        offer = self.stock.offer
        url = offer.product.url
        if url is None:
            return None
        if not url.startswith('http'):
            url = "http://" + url
        return url.replace('{token}', self.token) \
            .replace('{offerId}', humanize(offer.id)) \
            .replace('{email}', self.user.email)

    @property
    def isUserCancellable(self):
        if self.stock.beginningDatetime:
            event_starts_in_more_than_72_hours = self.stock.beginningDatetime > datetime.utcnow() + timedelta(
                hours=72)
            return event_starts_in_more_than_72_hours
        else:
            return True

    @staticmethod
    def restize_internal_error(ie):
        if 'tooManyBookings' in str(ie.orig):
            return ['global', 'La quantité disponible pour cette offre est atteinte.']
        elif 'insufficientFunds' in str(ie.orig):
            return ['insufficientFunds',
                    "Le solde de votre pass est insuffisant pour réserver cette offre."]
        return PcObject.restize_integrity_error(ie)

    @property
    def isEventExpired(self):
        if self.stock.beginningDatetime:
            event_start_time_is_over = self.stock.beginningDatetime <= datetime.utcnow()
            return event_start_time_is_over
        else:
            return False

    @property
    def thumbUrl(self):
        if self.recommendation:
            return self.recommendation.thumbUrl
        elif self.stock.offer.activeMediation:
            return self.stock.offer.activeMediation.thumbUrl
        else:
            return self.stock.offer.product.thumbUrl

    @property
    def mediation(self):
        if self.recommendation:
            return self.recommendation.mediation

    @property
    def mediationId(self):
        if self.recommendation:
            return self.recommendation.mediationId

    @property
    def qrCode(self):
        from domain.bookings import generate_qr_code
        offer = self.stock.offer
        if offer.isEvent:
            return generate_qr_code(self) if self.isEventExpired is False and self.isCancelled is False else None
        return generate_qr_code(self) if self.isUsed is False and self.isCancelled is False else None


class ActivationUser:
    CSV_HEADER = [
        'Prénom',
        'Nom',
        'Email',
        'Contremarque d\'activation'
    ]

    def __init__(self, booking: Booking):
        self.first_name = booking.user.firstName
        self.last_name = booking.user.lastName
        self.email = booking.user.email
        self.token = booking.token

    def as_csv_row(self):
        return [
            self.first_name,
            self.last_name,
            self.email,
            self.token
        ]


Booking.trig_ddl = """
    DROP FUNCTION IF EXISTS get_wallet_balance(user_id BIGINT);

    CREATE OR REPLACE FUNCTION get_wallet_balance(user_id BIGINT, only_used_bookings BOOLEAN)
    RETURNS NUMERIC(10,2) AS $$
    DECLARE
        sum_deposits NUMERIC ;
        sum_bookings NUMERIC ;
    BEGIN
        SELECT COALESCE(SUM(amount), 0)
        INTO sum_deposits
        FROM deposit
        WHERE "userId"=user_id;

        CASE
            only_used_bookings
        WHEN true THEN
            SELECT COALESCE(SUM(amount * quantity), 0)
            INTO sum_bookings
            FROM booking
            WHERE "userId"=user_id AND NOT "isCancelled" AND "isUsed" = true;
        WHEN false THEN
            SELECT COALESCE(SUM(amount * quantity), 0)
            INTO sum_bookings
            FROM booking
            WHERE "userId"=user_id AND NOT "isCancelled";
        END CASE;

        RETURN (sum_deposits - sum_bookings);
    END; $$
    LANGUAGE plpgsql;

    CREATE OR REPLACE FUNCTION check_booking()
    RETURNS TRIGGER AS $$
    DECLARE
        lastStockUpdate date := (SELECT "dateModified" FROM stock WHERE id=NEW."stockId");
    BEGIN
      IF EXISTS (SELECT "quantity" FROM stock WHERE id=NEW."stockId" AND "quantity" IS NOT NULL)
         AND (
             (SELECT "quantity" FROM stock WHERE id=NEW."stockId")
              <
              (SELECT SUM(quantity) FROM booking WHERE "stockId"=NEW."stockId" AND NOT "isCancelled")
              )
         THEN RAISE EXCEPTION 'tooManyBookings'
                    USING HINT = 'Number of bookings cannot exceed "stock.quantity"';
      END IF;

      IF (SELECT get_wallet_balance(NEW."userId", false) < 0)
      THEN RAISE EXCEPTION 'insufficientFunds'
                 USING HINT = 'The user does not have enough credit to book';
      END IF;

      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS booking_update ON booking;
    CREATE CONSTRAINT TRIGGER booking_update 
    AFTER INSERT 
    OR UPDATE OF quantity, amount, "isCancelled", "isUsed", "userId"  
    ON booking
    FOR EACH ROW EXECUTE PROCEDURE check_booking()
    """
event.listen(Booking.__table__,
             'after_create',
             DDL(Booking.trig_ddl))

Booking.trig_update_cancellationDate_on_isCancelled_ddl = """
    CREATE OR REPLACE FUNCTION save_cancellation_date()
    RETURNS TRIGGER AS $$
    BEGIN
        IF NEW."isCancelled" IS TRUE AND OLD."cancellationDate" IS NULL THEN
            NEW."cancellationDate" = NOW();
        ELSIF NEW."isCancelled" IS FALSE THEN
            NEW."cancellationDate" = NULL;
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS stock_update_cancellation_date ON booking;

    CREATE TRIGGER stock_update_cancellation_date
    BEFORE INSERT OR UPDATE ON booking
    FOR EACH ROW
    EXECUTE PROCEDURE save_cancellation_date()
    """

event.listen(Booking.__table__,
             'after_create',
             DDL(Booking.trig_update_cancellationDate_on_isCancelled_ddl))
