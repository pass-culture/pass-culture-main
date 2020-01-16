"""replace function wallet_balance

Revision ID: 6d93c35d097b
Revises: 72f3629849f0
Create Date: 2018-08-10 16:07:28.782900

"""
from alembic import op

# revision identifiers, used by Alembic.

revision = '6d93c35d097b'
down_revision = '72f3629849f0'
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
                     (SELECT COALESCE(SUM(amount * quantity), 0) FROM booking WHERE "userId"=user_id);
         END; $$
         LANGUAGE plpgsql;
    
         CREATE OR REPLACE FUNCTION check_booking()
         RETURNS TRIGGER AS $$
         BEGIN
           IF EXISTS (SELECT "available" FROM stock WHERE id=NEW."stockId" AND "available" IS NOT NULL)
              AND ((SELECT "available" FROM stock WHERE id=NEW."stockId")
                   < (SELECT COUNT(*) FROM booking WHERE "stockId"=NEW."stockId")) THEN
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
