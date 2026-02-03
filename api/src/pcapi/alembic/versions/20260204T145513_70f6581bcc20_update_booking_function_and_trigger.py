"""Update booking get_deposit_balance and booking_update"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "70f6581bcc20"
down_revision = "ce10822461a5"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.get_deposit_balance (deposit_id bigint, only_used_bookings boolean)
        RETURNS numeric
        LANGUAGE plpgsql
        AS $$
        DECLARE
            deposit_amount numeric := (SELECT CASE WHEN "expirationDate" > now() THEN amount ELSE 0 END amount FROM deposit WHERE id = deposit_id);
            sum_bookings numeric;
        BEGIN
            IF deposit_amount IS NULL
            THEN RAISE EXCEPTION 'the deposit was not found';
            END IF;

            SELECT
                COALESCE(SUM(COALESCE(booking_finance_incident."newTotalAmount" / 100,
                                booking.amount * booking.quantity)), 0) INTO sum_bookings
            FROM
                booking
                LEFT OUTER JOIN booking_finance_incident ON booking_finance_incident."bookingId" = booking.id
                LEFT OUTER JOIN finance_incident ON finance_incident.id = booking_finance_incident."incidentId" AND finance_incident."status" IN ('VALIDATED', 'INVOICED')
            WHERE
                booking."depositId" = deposit_id
                AND NOT booking.status = 'CANCELLED'
                AND (NOT only_used_bookings OR booking.status IN ('USED', 'PENDING_REIMBURSEMENT', 'REIMBURSED'));
            RETURN
                deposit_amount - sum_bookings;
        END
        $$;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION check_booking()
        RETURNS TRIGGER AS $$
        DECLARE
            lastStockUpdate date := (SELECT "dateModified" FROM stock WHERE id=NEW."stockId");
            deposit_id bigint := (SELECT booking."depositId" FROM booking WHERE booking.id=NEW.id);
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
            (
            -- If this is a new booking, we probably want to check the wallet.
            OLD IS NULL
            -- If we're updating an existing booking...
            OR (
                -- Check the wallet if we are changing the quantity or increasing the amount
                -- The backend should never do that, but let's be defensive.
                (NEW."quantity" != OLD."quantity" OR NEW."amount" > OLD."amount")
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
        OR UPDATE OF quantity, amount, status, "userId"
        ON booking
        FOR EACH ROW
        WHEN (NEW.status <> 'PENDING_REIMBURSEMENT' AND NEW.status <> 'REIMBURSED')
        EXECUTE PROCEDURE check_booking()
        """
    )


def downgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.get_deposit_balance (deposit_id bigint, only_used_bookings boolean)
        RETURNS numeric
        LANGUAGE plpgsql
        AS $$
        DECLARE
            deposit_amount numeric := (SELECT CASE WHEN "expirationDate" > now() THEN amount ELSE 0 END amount FROM deposit WHERE id = deposit_id);
            sum_bookings numeric;
        BEGIN
            IF deposit_amount IS NULL
            THEN RAISE EXCEPTION 'the deposit was not found';
            END IF;

            SELECT
                COALESCE(SUM(COALESCE(booking_finance_incident."newTotalAmount" / 100,
                                booking.amount * booking.quantity)), 0) INTO sum_bookings
            FROM
                booking
                LEFT OUTER JOIN booking_finance_incident ON booking_finance_incident."bookingId" = booking.id
                LEFT OUTER JOIN finance_incident ON finance_incident.id = booking_finance_incident."incidentId" AND finance_incident."status" IN ('VALIDATED', 'INVOICED')
            WHERE
                booking."depositId" = deposit_id
                AND NOT booking.status = 'CANCELLED'
                AND (NOT only_used_bookings OR booking.status IN ('USED', 'REIMBURSED'));
            RETURN
                deposit_amount - sum_bookings;
        END
        $$;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION check_booking()
        RETURNS TRIGGER AS $$
        DECLARE
            lastStockUpdate date := (SELECT "dateModified" FROM stock WHERE id=NEW."stockId");
            deposit_id bigint := (SELECT booking."depositId" FROM booking WHERE booking.id=NEW.id);
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
            (
            -- If this is a new booking, we probably want to check the wallet.
            OLD IS NULL
            -- If we're updating an existing booking...
            OR (
                -- Check the wallet if we are changing the quantity or increasing the amount
                -- The backend should never do that, but let's be defensive.
                (NEW."quantity" != OLD."quantity" OR NEW."amount" > OLD."amount")
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
        OR UPDATE OF quantity, amount, status, "userId"
        ON booking
        FOR EACH ROW
        WHEN NEW.status <> 'REIMBURSED'
        EXECUTE PROCEDURE check_booking()
        """
    )
