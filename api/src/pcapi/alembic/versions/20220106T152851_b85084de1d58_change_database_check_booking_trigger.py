"""change_database_check_booking_trigger
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "b85084de1d58"
down_revision = "525b100612c2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
          CREATE OR REPLACE FUNCTION check_booking()
    RETURNS TRIGGER AS $$
    DECLARE
        lastStockUpdate date := (SELECT "dateModified" FROM stock WHERE id=NEW."stockId");
        deposit_id bigint := (SELECT individual_booking."depositId" FROM booking LEFT JOIN individual_booking ON individual_booking.id = booking."individualBookingId" WHERE booking.id=NEW.id);
    BEGIN
    IF EXISTS (SELECT "quantity" FROM stock WHERE id=NEW."stockId" AND "quantity" IS NOT NULL)
        AND (
            (SELECT "quantity" FROM stock WHERE id=NEW."stockId")
            <
            (SELECT SUM(quantity) FROM booking WHERE "stockId"=NEW."stockId" AND status != 'CANCELLED')
            )
        THEN RAISE EXCEPTION 'tooManyBookings'
                    USING HINT = 'Number of bookings cannot exceed "stock.quantity"';
    END IF;

    IF (
        (NEW."educationalBookingId" IS NULL AND OLD."educationalBookingId" IS NULL)
        AND (NEW."individualBookingId" IS NOT NULL OR OLD."individualBookingId" IS NOT NULL)
        AND (
        -- If this is a new booking, we probably want to check the wallet.
        OLD IS NULL
        -- If we're updating an existing booking...
        OR (
            -- Check the wallet if we are changing the quantity or the amount
            -- The backend should never do that, but let's be defensive.
            (NEW."quantity" != OLD."quantity" OR NEW."amount" != OLD."amount")
            -- If amount and quantity are unchanged, we want to check the wallet
            -- only if we are UNcancelling a booking. (Users with no credits left
            -- should be able to cancel their booking. Also, their booking can
            -- be marked as used or not used.)
            OR (NEW.status != OLD.status AND OLD.status = 'CANCELLED' AND NEW.status != 'CANCELLED')
        )
        )
        AND (
            -- Allow to book free offers even with no credit left (or expired deposits)
            (deposit_id IS NULL AND NEW."amount" != 0)
            OR (deposit_id IS NOT NULL AND get_deposit_balance(deposit_id, false) < 0)
        )
    )
    THEN RAISE EXCEPTION 'insufficientFunds'
                USING HINT = 'The user does not have enough credit to book';
    END IF;

    RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS booking_update ON booking;
    CREATE CONSTRAINT TRIGGER booking_update
    AFTER INSERT
    OR UPDATE OF quantity, amount, status, "isUsed", "userId"
    ON booking
    FOR EACH ROW EXECUTE PROCEDURE check_booking()
      """
    )


def downgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION check_booking()
    RETURNS TRIGGER AS $$
    DECLARE
        lastStockUpdate date := (SELECT "dateModified" FROM stock WHERE id=NEW."stockId");
        deposit_id bigint := (SELECT individual_booking."depositId" FROM booking LEFT JOIN individual_booking ON individual_booking.id = booking."individualBookingId" WHERE booking.id=NEW.id);
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

    IF (
        (NEW."educationalBookingId" IS NULL AND OLD."educationalBookingId" IS NULL)
        AND (NEW."individualBookingId" IS NOT NULL OR OLD."individualBookingId" IS NOT NULL)
        AND (
        -- If this is a new booking, we probably want to check the wallet.
        OLD IS NULL
        -- If we're updating an existing booking...
        OR (
            -- Check the wallet if we are changing the quantity or the amount
            -- The backend should never do that, but let's be defensive.
            (NEW."quantity" != OLD."quantity" OR NEW."amount" != OLD."amount")
            -- If amount and quantity are unchanged, we want to check the wallet
            -- only if we are UNcancelling a booking. (Users with no credits left
            -- should be able to cancel their booking. Also, their booking can
            -- be marked as used or not used.)
            OR (NEW."isCancelled" != OLD."isCancelled" AND NOT NEW."isCancelled")
        )
        )
        AND (
            -- Allow to book free offers even with no credit left (or expired deposits)
            (deposit_id IS NULL AND NEW."amount" != 0)
            OR (deposit_id IS NOT NULL AND get_deposit_balance(deposit_id, false) < 0)
        )
    )
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
    )
