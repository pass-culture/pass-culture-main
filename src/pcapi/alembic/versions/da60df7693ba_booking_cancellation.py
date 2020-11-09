"""Add isCancelled to booking

Revision ID: da60df7693ba
Revises: 9f958c5e2435
Create Date: 2018-08-23 12:20:01.149618

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'da60df7693ba'
down_revision = '6d1eec337686'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
    """
      BEGIN TRANSACTION;
        ALTER TABLE "booking" ADD COLUMN "isCancelled" BOOLEAN DEFAULT False;
        CREATE OR REPLACE FUNCTION check_booking()
        RETURNS TRIGGER AS $$
        BEGIN
          IF EXISTS (SELECT "available" FROM stock WHERE id=NEW."stockId" AND "available" IS NOT NULL)
             AND ((SELECT "available" FROM stock WHERE id=NEW."stockId")
                  < (SELECT COUNT(*) FROM booking WHERE "stockId"=NEW."stockId" AND NOT "isCancelled")) THEN
              RAISE EXCEPTION 'tooManyBookings'
                    USING HINT = 'Number of bookings cannot exceed "stock.available"';
          END IF;
          IF (SELECT get_wallet_balance(NEW."userId") < 0)
          THEN RAISE EXCEPTION 'insufficientFunds'
                     USING HINT = 'The user does not have enough credit to book';
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        DROP TRIGGER IF EXISTS booking_update ON booking;
        CREATE CONSTRAINT TRIGGER booking_update AFTER INSERT OR UPDATE
        ON booking
        FOR EACH ROW EXECUTE PROCEDURE check_booking();
      COMMIT;
      """)


def downgrade():
    pass
