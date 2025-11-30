"""
Add counter tables and optimized check_booking trigger.

This migration solves a performance issue with the check_booking trigger on hypertables.
The original trigger runs:
1. SELECT SUM(quantity) FROM booking WHERE stockId = X  (for overbooking check)
2. get_deposit_balance() which aggregates bookings by depositId (for funds check)

Both queries must scan ALL time-based chunks because booking is partitioned by dateCreated,
not by stockId or depositId. For example, with ~250 chunks, this makes each insert ~11x slower.

Solution: Maintain counter tables with N * 1 lookups instead of N * num_chunks aggregations.
"""

from alembic import op


revision = "0002"
down_revision = "0001"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("""
        -- =====================================================================
        -- Stock booking counter (for overbooking check)
        -- =====================================================================

        CREATE TABLE IF NOT EXISTS stock_booking_count (
            stock_id BIGINT PRIMARY KEY REFERENCES stock(id) ON DELETE CASCADE,
            total_quantity INT NOT NULL DEFAULT 0,
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        -- Populate with existing booking counts
        INSERT INTO stock_booking_count (stock_id, total_quantity, updated_at)
        SELECT
            "stockId",
            COALESCE(SUM(quantity), 0)::INT,
            NOW()
        FROM booking
        WHERE status != 'CANCELLED'
        GROUP BY "stockId";

        -- =====================================================================
        -- Deposit spending counter (insufficient funds check)
        -- =====================================================================

        CREATE TABLE IF NOT EXISTS deposit_spending (
            deposit_id BIGINT PRIMARY KEY REFERENCES deposit(id) ON DELETE CASCADE,
            total_spent NUMERIC(10, 2) NOT NULL DEFAULT 0,
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );

        -- Populate with existing booking deposits
        -- Note: Finance?
        INSERT INTO deposit_spending (deposit_id, total_spent, updated_at)
        SELECT
            "depositId",
            COALESCE(SUM(amount * quantity), 0),
            NOW()
        FROM booking
        WHERE "depositId" IS NOT NULL AND status != 'CANCELLED'
        GROUP BY "depositId";

        -- =====================================================================
        -- Counter maintenance trigger
        -- =====================================================================

        CREATE OR REPLACE FUNCTION update_booking_counters()
        RETURNS TRIGGER AS $$
        DECLARE
            old_total NUMERIC;
            new_total NUMERIC;
        BEGIN
            IF TG_OP = 'INSERT' THEN
                IF NEW.status != 'CANCELLED' THEN
                    -- Update stock counter
                    INSERT INTO stock_booking_count (stock_id, total_quantity, updated_at)
                    VALUES (NEW."stockId", NEW.quantity, NOW())
                    ON CONFLICT (stock_id) DO UPDATE SET
                        total_quantity = stock_booking_count.total_quantity + NEW.quantity,
                        updated_at = NOW();

                    -- Update deposit spending
                    IF NEW."depositId" IS NOT NULL THEN
                        new_total := NEW.amount * NEW.quantity;
                        INSERT INTO deposit_spending (deposit_id, total_spent, updated_at)
                        VALUES (NEW."depositId", new_total, NOW())
                        ON CONFLICT (deposit_id) DO UPDATE SET
                            total_spent = deposit_spending.total_spent + new_total,
                            updated_at = NOW();
                    END IF;
                END IF;
                RETURN NEW;

            ELSIF TG_OP = 'UPDATE' THEN
                old_total := OLD.amount * OLD.quantity;
                new_total := NEW.amount * NEW.quantity;

                -- Handle status changes (cancellation/uncancellation)
                IF OLD.status != 'CANCELLED' AND NEW.status = 'CANCELLED' THEN
                    -- Booking cancelled: subtract from counters
                    UPDATE stock_booking_count
                    SET total_quantity = total_quantity - OLD.quantity, updated_at = NOW()
                    WHERE stock_id = OLD."stockId";

                    IF OLD."depositId" IS NOT NULL THEN
                        UPDATE deposit_spending
                        SET total_spent = total_spent - old_total, updated_at = NOW()
                        WHERE deposit_id = OLD."depositId";
                    END IF;

                ELSIF OLD.status = 'CANCELLED' AND NEW.status != 'CANCELLED' THEN
                    -- Booking uncancelled: add to counters
                    INSERT INTO stock_booking_count (stock_id, total_quantity, updated_at)
                    VALUES (NEW."stockId", NEW.quantity, NOW())
                    ON CONFLICT (stock_id) DO UPDATE SET
                        total_quantity = stock_booking_count.total_quantity + NEW.quantity,
                        updated_at = NOW();

                    IF NEW."depositId" IS NOT NULL THEN
                        INSERT INTO deposit_spending (deposit_id, total_spent, updated_at)
                        VALUES (NEW."depositId", new_total, NOW())
                        ON CONFLICT (deposit_id) DO UPDATE SET
                            total_spent = deposit_spending.total_spent + new_total,
                            updated_at = NOW();
                    END IF;

                ELSIF OLD.status != 'CANCELLED' AND NEW.status != 'CANCELLED' THEN
                    -- Active booking modified
                    IF OLD.quantity != NEW.quantity THEN
                        UPDATE stock_booking_count
                        SET total_quantity = total_quantity - OLD.quantity + NEW.quantity, updated_at = NOW()
                        WHERE stock_id = NEW."stockId";
                    END IF;

                    IF OLD."stockId" != NEW."stockId" THEN
                        UPDATE stock_booking_count
                        SET total_quantity = total_quantity - OLD.quantity, updated_at = NOW()
                        WHERE stock_id = OLD."stockId";
                        INSERT INTO stock_booking_count (stock_id, total_quantity, updated_at)
                        VALUES (NEW."stockId", NEW.quantity, NOW())
                        ON CONFLICT (stock_id) DO UPDATE SET
                            total_quantity = stock_booking_count.total_quantity + NEW.quantity,
                            updated_at = NOW();
                    END IF;

                    -- Handle deposit spending changes
                    IF old_total != new_total OR OLD."depositId" IS DISTINCT FROM NEW."depositId" THEN
                        IF OLD."depositId" IS NOT NULL THEN
                            UPDATE deposit_spending
                            SET total_spent = total_spent - old_total, updated_at = NOW()
                            WHERE deposit_id = OLD."depositId";
                        END IF;
                        IF NEW."depositId" IS NOT NULL THEN
                            INSERT INTO deposit_spending (deposit_id, total_spent, updated_at)
                            VALUES (NEW."depositId", new_total, NOW())
                            ON CONFLICT (deposit_id) DO UPDATE SET
                                total_spent = deposit_spending.total_spent + new_total,
                                updated_at = NOW();
                        END IF;
                    END IF;
                END IF;
                RETURN NEW;

            ELSIF TG_OP = 'DELETE' THEN
                IF OLD.status != 'CANCELLED' THEN
                    UPDATE stock_booking_count
                    SET total_quantity = total_quantity - OLD.quantity, updated_at = NOW()
                    WHERE stock_id = OLD."stockId";

                    IF OLD."depositId" IS NOT NULL THEN
                        old_total := OLD.amount * OLD.quantity;
                        UPDATE deposit_spending
                        SET total_spent = total_spent - old_total, updated_at = NOW()
                        WHERE deposit_id = OLD."depositId";
                    END IF;
                END IF;
                RETURN OLD;
            END IF;

            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;

        -- Replace old trigger
        DROP TRIGGER IF EXISTS booking_count_trigger ON booking;
        CREATE TRIGGER booking_counters_trigger
        AFTER INSERT OR UPDATE OR DELETE ON booking
        FOR EACH ROW
        EXECUTE FUNCTION update_booking_counters();

        -- =====================================================================
        -- New get_deposit_balance function
        -- =====================================================================

        CREATE OR REPLACE FUNCTION public.get_deposit_balance(deposit_id bigint, only_used_bookings boolean)
        RETURNS numeric AS $$
        DECLARE
            deposit_amount numeric;
            spent numeric;
        BEGIN
            -- Get deposit amount (if not expired)
            SELECT CASE WHEN "expirationDate" > now() THEN amount ELSE 0 END
            INTO deposit_amount
            FROM deposit WHERE id = deposit_id;
            IF deposit_amount IS NULL THEN
                RAISE EXCEPTION 'Deposit was not found';
            END IF;

            -- For only_used_bookings, we still need the original query
            -- as the counter tracks all non-cancelled bookings
            IF only_used_bookings THEN
                SELECT COALESCE(SUM(COALESCE(booking_finance_incident."newTotalAmount" / 100,
                                booking.amount * booking.quantity)), 0)
                INTO spent
                FROM booking
                LEFT OUTER JOIN booking_finance_incident ON booking_finance_incident."bookingId" = booking.id
                LEFT OUTER JOIN finance_incident ON finance_incident.id = booking_finance_incident."incidentId"
                    AND finance_incident."status" IN ('VALIDATED', 'INVOICED')
                WHERE booking."depositId" = deposit_id
                    AND booking.status != 'CANCELLED'
                    AND booking.status IN ('USED', 'REIMBURSED');
            ELSE
                -- Use the fast counter lookup
                SELECT COALESCE(total_spent, 0) INTO spent
                FROM deposit_spending
                WHERE deposit_spending.deposit_id = get_deposit_balance.deposit_id;

                IF spent IS NULL THEN
                    spent := 0;
                END IF;
            END IF;

            RETURN deposit_amount - spent;
        END;
        $$ LANGUAGE plpgsql;

        -- =====================================================================
        -- Index on booking.id for fast lookups
        -- =====================================================================

        -- The hypertable conversion drops the primary key on id.
        -- We need an index for the check_booking trigger to look up depositId.
        CREATE INDEX IF NOT EXISTS idx_booking_id ON booking(id);

        -- =====================================================================
        -- New check_booking function
        -- =====================================================================

        CREATE OR REPLACE FUNCTION check_booking()
        RETURNS TRIGGER AS $$
        DECLARE
            stock_quantity int;
            current_bookings int;
            pending_quantity int;
        BEGIN
            SELECT "quantity" INTO stock_quantity FROM stock WHERE id = NEW."stockId";

            -- Only check if stock is not unlimited (NULL)
            IF stock_quantity IS NOT NULL THEN
                SELECT COALESCE(total_quantity, 0)
                INTO current_bookings
                FROM stock_booking_count
                WHERE stock_id = NEW."stockId";
                IF current_bookings IS NULL THEN
                    current_bookings := 0;
                END IF;

                -- Calculate pending quantity for this booking
                -- TODO (igabriele): Double-check this rule.
                IF OLD IS NULL THEN
                    pending_quantity := NEW.quantity;
                ELSIF OLD.status = 'CANCELLED' AND NEW.status != 'CANCELLED' THEN
                    pending_quantity := NEW.quantity;
                ELSIF OLD.status != 'CANCELLED' AND NEW.status != 'CANCELLED' THEN
                    pending_quantity := NEW.quantity - OLD.quantity;
                ELSE
                    pending_quantity := 0;
                END IF;

                IF stock_quantity < current_bookings + pending_quantity THEN
                    RAISE EXCEPTION 'tooManyBookings'
                        USING HINT = 'Number of bookings cannot exceed "stock.quantity"';
                END IF;
            END IF;

            -- Check user funds
            -- TODO (igabriele): Double-check this rule.
            IF (
                (
                    OLD IS NULL
                    OR (
                        (NEW."quantity" != OLD."quantity" OR NEW."amount" > OLD."amount")
                        OR (NEW.status != OLD.status AND OLD.status = 'CANCELLED' AND NEW.status != 'CANCELLED')
                    )
                )
                AND (
                    (NEW."depositId" IS NULL AND NEW."amount" != 0)
                    OR (NEW."depositId" IS NOT NULL AND get_deposit_balance(NEW."depositId", false) < 0)
                )
            )
            THEN RAISE EXCEPTION 'insufficientFunds'
                USING HINT = 'The user does not have enough credit to book';
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)


def downgrade() -> None:
    op.execute("""
        DROP TRIGGER IF EXISTS booking_counters_trigger ON booking;

        DROP FUNCTION IF EXISTS update_booking_counters();

        DROP TABLE IF EXISTS deposit_spending;
        DROP TABLE IF EXISTS stock_booking_count;

        DO $$
        BEGIN
            RAISE EXCEPTION 'Original functions won''t be reverted automatically.';
        END
        $$;
    """)
