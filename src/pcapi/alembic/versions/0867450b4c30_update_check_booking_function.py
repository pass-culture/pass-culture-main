"""Update `check_booking`

Revision ID: 0867450b4c30
Revises: 2b860ecd3072
Create Date: 2021-02-08 10:58:14.217608

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "0867450b4c30"
down_revision = "2b860ecd3072"
branch_labels = None
depends_on = None


def upgrade():
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
            -- only if we are UNcancelling a booking (which the backend should never
            -- do, but let's be defensive). Users with no credits left should
            -- be able to cancel their booking. Also, their booking can
            -- be marked as used or not used.
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


def downgrade():
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
      IF (SELECT get_wallet_balance(NEW."userId", false) < 0)
      THEN RAISE EXCEPTION 'insufficientFunds'
                 USING HINT = 'The user does not have enough credit to book';
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
        """
    )
