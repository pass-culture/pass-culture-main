"""Add parameter to signature of function get_wallet_balance

Revision ID: 573342f77706
Revises: 24f901d09066
Create Date: 2018-12-20 13:56:01.675719

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '573342f77706'
down_revision = '39005c57b66d'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        DROP FUNCTION get_wallet_balance(user_id BIGINT);
    
        CREATE OR REPLACE FUNCTION get_wallet_balance(user_id BIGINT, only_used_bookings BOOLEAN)
        RETURNS NUMERIC(10,2) AS $$
        DECLARE
            sum_deposits NUMERIC ;
            sum_bookings NUMERIC ;
        BEGIN
            SELECT COALESCE(SUM(amount), 0)
            INTO sum_deposits
            FROM deposit
            WHERE "userId"=user_id;
            
            CASE
                only_used_bookings
            WHEN true THEN
                SELECT COALESCE(SUM(amount * quantity), 0)
                INTO sum_bookings
                FROM booking
                WHERE "userId"=user_id AND NOT "isCancelled" AND "isUsed" = true;
            WHEN false THEN
                SELECT COALESCE(SUM(amount * quantity), 0)
                INTO sum_bookings
                FROM booking
                WHERE "userId"=user_id AND NOT "isCancelled";
            END CASE;
            
            RETURN (sum_deposits - sum_bookings);            
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
        """
    )


def downgrade():
    pass
