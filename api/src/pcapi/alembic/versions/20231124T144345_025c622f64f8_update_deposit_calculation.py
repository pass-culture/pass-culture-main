"""
Update `get_deposit_balance` function
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "025c622f64f8"
down_revision = "1fb084a51b0d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
     CREATE OR REPLACE FUNCTION public.get_deposit_balance(deposit_id bigint, only_used_bookings boolean)
    RETURNS numeric
    LANGUAGE plpgsql
    AS
    $$
    DECLARE
        deposit_amount bigint := (SELECT CASE
                                             WHEN "expirationDate" > now()
                                                 THEN amount
                                             ELSE 0 END amount
                                  FROM deposit
                                  WHERE id = deposit_id);
        sum_bookings   numeric;
    BEGIN
        IF deposit_amount IS NULL
        THEN
            RAISE EXCEPTION 'the deposit was not found';
        END IF;
    
        SELECT COALESCE(SUM(COALESCE(booking_finance_incident."newTotalAmount" / 100,
                            booking.amount * booking.quantity)), 0)
        INTO sum_bookings
        FROM
            booking
            LEFT OUTER JOIN booking_finance_incident ON booking_finance_incident."bookingId" = booking.id
            LEFT OUTER JOIN finance_incident ON  finance_incident.id = booking_finance_incident."incidentId" AND finance_incident."status" =  'VALIDATED'
        WHERE booking."depositId" = deposit_id
          AND NOT booking.status = 'CANCELLED'
          AND (NOT only_used_bookings OR booking.status IN ('USED', 'REIMBURSED'));
        RETURN
            deposit_amount - sum_bookings;
    END
    $$;
    """
    )


def downgrade() -> None:
    op.execute(
        """
    CREATE OR REPLACE FUNCTION public.get_deposit_balance(deposit_id bigint, only_used_bookings boolean) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
    DECLARE
        deposit_amount bigint := (SELECT CASE WHEN "expirationDate" > now() THEN amount ELSE 0 END amount 
        FROM deposit WHERE id = deposit_id);
        sum_bookings numeric;
    BEGIN
        IF deposit_amount IS NULL
        THEN RAISE EXCEPTION 'the deposit was not found';
        END IF;

        SELECT
            COALESCE(SUM(amount * quantity), 0) INTO sum_bookings
        FROM
            booking
        WHERE
            booking."depositId" = deposit_id
            AND NOT booking.status = 'CANCELLED'
            AND (NOT only_used_bookings OR booking.status in ('USED', 'REIMBURSED'));
        RETURN
            deposit_amount - sum_bookings;
        END;
    $$;
    """
    )
