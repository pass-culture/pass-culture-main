"""Add new single-parameter get_wallet_balance function.

It replaces the legacy double-parameter version 'get_wallet_balance(user_id bigint, only_used_bookings boolean)'
which is dropped in a corresponding post-deployment migration:
20260909T112558_3a5ee54be21c_delete_get_wallet_balance_with_double_param_function.
"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "48232008761a"
down_revision = "6993fbbec133"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(
            """
            CREATE OR REPLACE FUNCTION public.get_wallet_balance(user_id bigint) RETURNS numeric
                LANGUAGE plpgsql STABLE
                AS $$
                    DECLARE
                        deposit_id bigint;
                        deposit_amount numeric;
                        spent_amount numeric;
                    BEGIN
                        SELECT id, amount
                        INTO deposit_id, deposit_amount
                        FROM deposit
                        WHERE
                            "userId" = user_id
                            AND (
                                "expirationDate" IS NULL
                                OR "expirationDate" > now()
                            )
                        ORDER BY "expirationDate" DESC
                        LIMIT 1;

                        IF deposit_id IS NULL THEN
                            RETURN NULL;
                        END IF;

                        -- One row per booking: a booking is charged its partial incident amount when it has one
                        -- (first VALIDATED or INVOICED incident with a non-zero new total), its full price otherwise.
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
                                ORDER BY booking_finance_incident.id
                                LIMIT 1
                            ) AS partial_incident ON TRUE
                        WHERE
                            booking."depositId" = deposit_id
                            AND booking.status <> 'CANCELLED'
                        ;

                        RETURN GREATEST(deposit_amount - spent_amount, 0);
                    END;
                    $$;
            """
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("DROP FUNCTION IF EXISTS public.get_wallet_balance(bigint)")
