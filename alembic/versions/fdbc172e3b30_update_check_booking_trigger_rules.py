"""update_check_booking_trigger_rules

Revision ID: fdbc172e3b30
Revises: 8e1f487e2d23
Create Date: 2019-07-24 14:41:13.167987

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'fdbc172e3b30'
down_revision = 'a5a9a6e32ae7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('booking', sa.Column('dateUsed', sa.DateTime(), nullable=True))
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


def downgrade():
    op.drop_column('booking', 'dateUsed')
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

