"""update_check_booking_remove_is_used_condition

Revision ID: eb60e72463f1
Revises: 2fb60c9897d3
Create Date: 2020-03-18 10:16:06.456505

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'eb60e72463f1'
down_revision = '2fb60c9897d3'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE OR REPLACE FUNCTION check_booking()
        RETURNS TRIGGER AS $$
        BEGIN
          IF EXISTS (SELECT "available" FROM stock WHERE id=NEW."stockId" AND "available" IS NOT NULL)
             AND (
                (SELECT "available" FROM stock WHERE id=NEW."stockId") <
                (
                  SELECT SUM(quantity)
                  FROM booking
                  WHERE "stockId"=NEW."stockId"
                  AND NOT "isCancelled"
                )
              ) THEN
              RAISE EXCEPTION 'tooManyBookings'
                    USING HINT = 'Number of bookings cannot exceed "stock.available"';
          END IF;

          IF (SELECT get_wallet_balance(NEW."userId", false) < 0)
          THEN RAISE EXCEPTION 'insufficientFunds'
                     USING HINT = 'The user does not have enough credit to book';
          END IF;

          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS booking_update ON booking;
        CREATE CONSTRAINT TRIGGER booking_update AFTER INSERT OR UPDATE
        ON booking
        FOR EACH ROW EXECUTE PROCEDURE check_booking()
        """ + ';')


def downgrade():
    op.execute("""
        CREATE OR REPLACE FUNCTION check_booking()
        RETURNS TRIGGER AS $$
        DECLARE
            lastStockUpdate date := (SELECT "dateModified" FROM stock WHERE id=NEW."stockId");
        BEGIN
          IF EXISTS (SELECT "available" FROM stock WHERE id=NEW."stockId" AND "available" IS NOT NULL)
             AND (
                (SELECT "available" FROM stock WHERE id=NEW."stockId") <
                (
                  SELECT SUM(quantity)
                  FROM booking
                  WHERE "stockId"=NEW."stockId"
                  AND (
                    NOT "isCancelled" AND NOT "isUsed"
                    OR ("isUsed" AND "dateUsed" > lastStockUpdate)
                  )
                )
              ) THEN
              RAISE EXCEPTION 'tooManyBookings'
                    USING HINT = 'Number of bookings cannot exceed "stock.available"';
          END IF;

          IF (SELECT get_wallet_balance(NEW."userId", false) < 0)
          THEN RAISE EXCEPTION 'insufficientFunds'
                     USING HINT = 'The user does not have enough credit to book';
          END IF;

          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS booking_update ON booking;
        CREATE CONSTRAINT TRIGGER booking_update AFTER INSERT OR UPDATE
        ON booking
        FOR EACH ROW EXECUTE PROCEDURE check_booking()
        """ + ';')
