"""Rename_Stock_column_available_to_quantity

Revision ID: da973e646e06
Revises: 5bccb7eb3d68
Create Date: 2020-04-02 08:44:57.934373

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'da973e646e06'
down_revision = '5bccb7eb3d68'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('stock', 'available', new_column_name='quantity')
    op.alter_column('allocine_venue_provider', 'available', new_column_name='quantity')

    op.execute("""
        UPDATE stock
        SET fieldsUpdated = replace(value, 'available', 'quantity')
    """)

    op.execute(
        """
        CREATE OR REPLACE FUNCTION save_stock_modification_date()
        RETURNS TRIGGER AS $$
        BEGIN
          IF NEW.quantity != OLD.quantity THEN
            NEW."dateModified" = NOW();
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS stock_update_modification_date ON stock;
        
        CREATE TRIGGER stock_update_modification_date
        BEFORE UPDATE ON stock
        FOR EACH ROW
        EXECUTE PROCEDURE save_stock_modification_date()
        """ + ';')

    op.execute(
        """
        CREATE OR REPLACE FUNCTION offer_has_at_least_one_bookable_stock(offer_id BIGINT)
        RETURNS SETOF INTEGER AS
        $body$
        BEGIN
           RETURN QUERY
           SELECT 1
              FROM stock
             WHERE stock."offerId" = offer_id
               AND stock."isSoftDeleted" = FALSE
               AND (stock."beginningDatetime" > NOW()
                    OR stock."beginningDatetime" IS NULL)
               AND (stock."bookingLimitDatetime" > NOW()
                    OR stock."bookingLimitDatetime" IS NULL)
               AND (stock.quantity IS NULL
                    OR (SELECT greatest(stock.quantity - COALESCE(sum(booking.quantity), 0),0)
                          FROM booking
                         WHERE booking."stockId" = stock.id
                           AND booking."isCancelled" = FALSE
                        ) > 0
                    );
        END
        $body$
        LANGUAGE plpgsql;
            """
    )

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
    
        DROP TRIGGER IF EXISTS booking_update ON booking;
        CREATE CONSTRAINT TRIGGER booking_update AFTER INSERT OR UPDATE
        ON booking
        FOR EACH ROW EXECUTE PROCEDURE check_booking()
        """
    )


def downgrade():
    op.alter_column('stock', 'quantity', new_column_name='available')
    op.alter_column('allocine_venue_provider', 'quantity', new_column_name='available')

    op.execute("""
        UPDATE stock
        SET fieldsUpdated = replace(value, 'quantity', 'available')
    """)

    op.execute(
        """
        CREATE OR REPLACE FUNCTION save_stock_modification_date()
        RETURNS TRIGGER AS $$
        BEGIN
          IF NEW.available != OLD.available THEN
            NEW."dateModified" = NOW();
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS stock_update_modification_date ON stock;
        
        CREATE TRIGGER stock_update_modification_date
        BEFORE UPDATE ON stock
        FOR EACH ROW
        EXECUTE PROCEDURE save_stock_modification_date()
        """ + ';')

    op.execute(
        """
        CREATE OR REPLACE FUNCTION offer_has_at_least_one_bookable_stock(offer_id BIGINT)
        RETURNS SETOF INTEGER AS
        $body$
        BEGIN
           RETURN QUERY
           SELECT 1
              FROM stock
             WHERE stock."offerId" = offer_id
               AND stock."isSoftDeleted" = FALSE
               AND (stock."beginningDatetime" > NOW()
                    OR stock."beginningDatetime" IS NULL)
               AND (stock."bookingLimitDatetime" > NOW()
                    OR stock."bookingLimitDatetime" IS NULL)
               AND (stock.available IS NULL
                    OR (SELECT greatest(stock.available - COALESCE(sum(booking.quantity), 0),0)
                          FROM booking
                         WHERE booking."stockId" = stock.id
                           AND booking."isCancelled" = FALSE
                        ) > 0
                    );
        END
        $body$
        LANGUAGE plpgsql;
            """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION check_booking()
        RETURNS TRIGGER AS $$
        DECLARE
            lastStockUpdate date := (SELECT "dateModified" FROM stock WHERE id=NEW."stockId");
        BEGIN
          IF EXISTS (SELECT "available" FROM stock WHERE id=NEW."stockId" AND "available" IS NOT NULL)
             AND (
                 (SELECT "available" FROM stock WHERE id=NEW."stockId")
                  <
                  (SELECT SUM(quantity) FROM booking WHERE "stockId"=NEW."stockId" AND NOT "isCancelled")
                  )
             THEN RAISE EXCEPTION 'tooManyBookings'
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
