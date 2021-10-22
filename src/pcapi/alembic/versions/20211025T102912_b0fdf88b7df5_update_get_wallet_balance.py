"""update_get_wallet_balance
"""
from alembic import op


revision = "b0fdf88b7df5"
down_revision = "5641f4266d73"
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
                AND NOT booking."isCancelled"
                AND (NOT only_used_bookings OR booking."isUsed" = TRUE);
            RETURN
                deposit_amount - sum_bookings;
            END;
        $$
        LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.get_wallet_balance (user_id bigint, only_used_bookings boolean)
            RETURNS numeric
            AS $$
        DECLARE
            deposit_id bigint := (SELECT deposit.id FROM deposit WHERE "userId" = user_id  AND "expirationDate" > now());
        BEGIN
            RETURN
                CASE WHEN deposit_id IS NOT NULL THEN get_deposit_balance(deposit_id, only_used_bookings) ELSE 0 END;
        END;
        $$
        LANGUAGE plpgsql;
    """
    )


def downgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.get_wallet_balance (user_id bigint, only_used_bookings boolean)
            RETURNS numeric
            LANGUAGE plpgsql
            AS $$
        DECLARE
            sum_deposits numeric;
            sum_bookings numeric;
        BEGIN
            SELECT
                COALESCE(SUM(amount), 0) INTO sum_deposits
            FROM
                deposit
            WHERE
                "userId" = user_id
                AND ("expirationDate" > now()
                    OR "expirationDate" IS NULL);
            CASE only_used_bookings
            WHEN TRUE THEN
                SELECT
                    COALESCE(SUM(amount * quantity), 0) INTO sum_bookings
                FROM
                    booking
                WHERE
                    "userId" = user_id
                    AND NOT "isCancelled"
                    AND "isUsed" = TRUE;
            WHEN FALSE THEN
                SELECT
                    COALESCE(SUM(amount * quantity), 0) INTO sum_bookings
                FROM
                    booking
                WHERE
                    "userId" = user_id
                    AND NOT "isCancelled";
            END CASE;
            RETURN (sum_deposits - sum_bookings);
            END;
        $$;
        """
    )
    op.execute("DROP FUNCTION IF EXISTS get_deposit_balance")
