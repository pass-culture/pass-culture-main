"""Permit to decrease booking value even if the beneficiary does not have a valid deposit anymore.
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a006ff4ea0bf"
down_revision = "9b8702ecd055"
branch_labels = None
depends_on = None


def upgrade() -> None:
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
        """
    )


def downgrade() -> None:
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
        """
    )
