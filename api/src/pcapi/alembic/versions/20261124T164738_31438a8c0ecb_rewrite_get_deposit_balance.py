"""Create new get_deposit_balance with one param"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "31438a8c0ecb"
down_revision = "ed059b9cf77e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(
            """
                CREATE OR REPLACE FUNCTION public.get_deposit_balance (deposit_id bigint)
                    RETURNS numeric
                    AS $$
                DECLARE
                    deposit_amount numeric := (SELECT CASE WHEN "expirationDate" > now() THEN amount ELSE 0 END amount FROM deposit WHERE id = deposit_id);
                    spent_amount numeric;
                BEGIN
                    SELECT
                        COALESCE(SUM(COALESCE(partial_incident.new_total_amount, booking.amount * booking.quantity)), 0)
                    INTO spent_amount
                    FROM
                        booking
                        LEFT OUTER JOIN LATERAL (
                            SELECT booking_finance_incident."newTotalAmount" * 0.01 AS new_total_amount
                            FROM
                                booking_finance_incident
                                JOIN finance_incident ON finance_incident.id = booking_finance_incident."incidentId"
                            WHERE
                                booking_finance_incident."bookingId" = booking.id
                                AND booking_finance_incident."newTotalAmount" > 0
                                AND finance_incident.status IN ('VALIDATED', 'INVOICED')
                                AND finance_incident.kind = 'OVERPAYMENT'
                            LIMIT 1
                        ) AS partial_incident ON TRUE
                    WHERE
                        booking."depositId" = deposit_id
                        AND booking.status <> 'CANCELLED'
                    ;

                    RETURN deposit_amount - spent_amount;
                END;
                $$
                LANGUAGE plpgsql;
            """
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("select 1 -- squawk:ignore-next-statement")
        op.execute("DROP FUNCTION IF EXISTS public.get_deposit_balance(bigint)")
