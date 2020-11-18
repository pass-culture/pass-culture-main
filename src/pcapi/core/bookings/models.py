from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DDL
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import event
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from pcapi.models.db import Model
from pcapi.models.pc_object import PcObject
from pcapi.models.versioned_mixin import VersionedMixin
from pcapi.utils.human_ids import humanize


class Booking(PcObject, Model, VersionedMixin):
    __tablename__ = "booking"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    dateCreated = Column(DateTime, nullable=False, default=datetime.utcnow)

    dateUsed = Column(DateTime, nullable=True)

    recommendationId = Column(BigInteger, ForeignKey("recommendation.id"), index=True)

    recommendation = relationship("Recommendation", foreign_keys=[recommendationId], backref="bookings")

    stockId = Column(BigInteger, ForeignKey("stock.id"), index=True, nullable=False)

    stock = relationship("Stock", foreign_keys=[stockId], backref="bookings")

    quantity = Column(Integer, nullable=False, default=1)

    token = Column(String(6), unique=True, nullable=False)

    userId = Column(BigInteger, ForeignKey("user.id"), index=True, nullable=False)

    user = relationship("UserSQLEntity", foreign_keys=[userId], backref="userBookings")

    amount = Column(Numeric(10, 2), nullable=False)

    isCancelled = Column(Boolean, nullable=False, server_default=expression.false(), default=False)

    cancellationDate = Column(DateTime, nullable=True)

    isUsed = Column(Boolean, nullable=False, default=False)

    confirmationDate = Column(DateTime, nullable=True)

    @property
    def total_amount(self):
        return self.amount * self.quantity

    # FIXME: many functions here are only used when serializing
    # bookings in the web API. They can be moved elsewhere once we
    # have replaced the auto-magic serialization ("includes").
    @property
    def completedUrl(self):
        offer = self.stock.offer
        url = offer.url
        if url is None:
            return None
        if not url.startswith("http"):
            url = "http://" + url
        return (
            url.replace("{token}", self.token)
            .replace("{offerId}", humanize(offer.id))
            .replace("{email}", self.user.email)
        )

    @staticmethod
    def restize_internal_error(ie):
        if "tooManyBookings" in str(ie.orig):
            return ["global", "La quantité disponible pour cette offre est atteinte."]
        elif "insufficientFunds" in str(ie.orig):
            return ["insufficientFunds", "Le solde de votre pass est insuffisant pour réserver cette offre."]
        return PcObject.restize_integrity_error(ie)

    @property
    def isEventExpired(self):
        return self.stock.isEventExpired

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
        from . import api  # avoid import loop

        offer = self.stock.offer
        if offer.isEvent:
            if self.isEventExpired or self.isCancelled:
                return None
            return api.generate_qr_code(self.token, self.stock.offer.extraData)
        if self.isUsed or self.isCancelled:
            return None
        return api.generate_qr_code(self.token, self.stock.offer.extraData)

    @hybrid_property
    def isConfirmed(self):
        return self.confirmationDate and self.confirmationDate <= datetime.utcnow()


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
event.listen(Booking.__table__, "after_create", DDL(Booking.trig_ddl))

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

event.listen(Booking.__table__, "after_create", DDL(Booking.trig_update_cancellationDate_on_isCancelled_ddl))
