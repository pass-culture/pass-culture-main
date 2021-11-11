"""update_check_booking_trigger

Revision ID: 9feb58815d16
Revises: f91ee203522a
Create Date: 2021-06-29 13:58:34.596976

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "9feb58815d16"
down_revision = "f91ee203522a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
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

      IF (
        (NEW."educationalBookingId" IS NULL AND OLD."educationalBookingId" IS NULL)
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
        -- Allow to book free offers even with no credit left (or expired deposits)
        AND (NEW."amount" != 0)
        AND (get_wallet_balance(NEW."userId", false) < 0)
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
            OR (NEW."isCancelled" != OLD."isCancelled" AND NOT NEW."isCancelled")
          )
        )
        -- Allow to book free offers even with no credit left (or expired deposits)
        AND (NEW."amount" != 0)
        AND (get_wallet_balance(NEW."userId", false) < 0)
      )
      THEN RAISE EXCEPTION 'insufficientFunds'
                 USING HINT = 'The user does not have enough credit to book';
      END IF;

      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
    )
