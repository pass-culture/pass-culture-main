"""remove_isUsed_column_from_booking_trigger
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "b7a2d1d87495"
down_revision = "b400b5a91243"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
      CREATE OR REPLACE FUNCTION public.get_deposit_balance (deposit_id bigint, only_used_bookings boolean)
        RETURNS numeric
        AS $$
    DECLARE
        deposit_amount bigint := (SELECT CASE WHEN ("expirationDate" > now() OR "expirationDate" IS NULL) THEN amount ELSE 0 END amount FROM deposit WHERE id = deposit_id);
        sum_bookings numeric;
    BEGIN
        IF deposit_amount IS NULL
        THEN RAISE EXCEPTION 'the deposit was not found';
        END IF;

        SELECT
            COALESCE(SUM(amount * quantity), 0) INTO sum_bookings
        FROM
            booking
            JOIN individual_booking ON (booking."individualBookingId" = individual_booking.id)
        WHERE
            individual_booking."depositId" = deposit_id
            AND NOT booking.status = 'CANCELLED'
            AND (NOT only_used_bookings OR booking.status in ('USED', 'REIMBURSED'));
        RETURN
            deposit_amount - sum_bookings;
        END;
    $$
    LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS booking_update ON booking;
    CREATE CONSTRAINT TRIGGER booking_update
    AFTER INSERT
    OR UPDATE OF quantity, amount, status, "userId"
    ON booking
    FOR EACH ROW EXECUTE PROCEDURE check_booking()
    """
    )


def downgrade() -> None:
    op.execute(
        """
      CREATE OR REPLACE FUNCTION public.get_deposit_balance (deposit_id bigint, only_used_bookings boolean)
        RETURNS numeric
        AS $$
    DECLARE
        deposit_amount bigint := (SELECT CASE WHEN ("expirationDate" > now() OR "expirationDate" IS NULL) THEN amount ELSE 0 END amount FROM deposit WHERE id = deposit_id);
        sum_bookings numeric;
    BEGIN
        IF deposit_amount IS NULL
        THEN RAISE EXCEPTION 'the deposit was not found';
        END IF;

        SELECT
            COALESCE(SUM(amount * quantity), 0) INTO sum_bookings
        FROM
            booking
            JOIN individual_booking ON (booking."individualBookingId" = individual_booking.id)
        WHERE
            individual_booking."depositId" = deposit_id
            AND NOT booking.status = 'CANCELLED'
            AND (NOT only_used_bookings OR booking."isUsed" = TRUE);
        RETURN
            deposit_amount - sum_bookings;
        END;
    $$
    LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS booking_update ON booking;
    CREATE CONSTRAINT TRIGGER booking_update
    AFTER INSERT
    OR UPDATE OF quantity, amount, status, "isUsed", "userId"
    ON booking
    FOR EACH ROW EXECUTE PROCEDURE check_booking()
    """
    )
