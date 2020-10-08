"""Don't include cancelled bookings in balance, take booking quantities into account for remaining stock

Revision ID: 4fc1f5367b4c
Revises: 6b0fedcc7b6a
Create Date: 2018-10-15 06:14:17.871585

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '4fc1f5367b4c'
down_revision = 'd176385d379e'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
         CREATE OR REPLACE FUNCTION get_wallet_balance(user_id BIGINT)
         RETURNS NUMERIC(10,2) AS $$
         BEGIN
             RETURN 
                     (SELECT COALESCE(SUM(amount), 0) FROM deposit WHERE "userId"=user_id)
                     -
                     (SELECT COALESCE(SUM(amount * quantity), 0) FROM booking WHERE "userId"=user_id AND NOT "isCancelled");
         END; $$
         LANGUAGE plpgsql;
    
         CREATE OR REPLACE FUNCTION check_booking()
         RETURNS TRIGGER AS $$
         BEGIN
           IF EXISTS (SELECT "available" FROM stock WHERE id=NEW."stockId" AND "available" IS NOT NULL)
              AND ((SELECT "available" FROM stock WHERE id=NEW."stockId")
                   < (SELECT SUM(quantity) FROM booking WHERE "stockId"=NEW."stockId" AND NOT "isCancelled")) THEN
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
         FOR EACH ROW EXECUTE PROCEDURE check_booking()
         """ + ';')


def downgrade():
    pass
