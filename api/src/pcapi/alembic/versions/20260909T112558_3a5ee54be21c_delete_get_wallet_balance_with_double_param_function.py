"""Delete legacy double-parameter get_wallet_balance function.

It is replaced by the new single-parameter get_wallet_balance function:
20260909T111348_48232008761a_add_get_wallet_balance_with_single_param_function
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3a5ee54be21c"
down_revision = "1abd7f75118f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("DROP FUNCTION IF EXISTS public.get_wallet_balance(bigint, boolean)")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(
            """
            CREATE FUNCTION public.get_wallet_balance(user_id bigint, only_used_bookings boolean) RETURNS numeric
                LANGUAGE plpgsql
                AS $$
                    DECLARE
                        deposit_id bigint := (SELECT deposit.id FROM deposit WHERE "userId" = user_id AND "expirationDate" > now() ORDER BY "expirationDate" DESC LIMIT 1);
                    BEGIN
                        RETURN
                            CASE WHEN deposit_id IS NOT NULL THEN get_deposit_balance(deposit_id, only_used_bookings) ELSE 0 END;
                    END;
                    $$;
            """
        )
