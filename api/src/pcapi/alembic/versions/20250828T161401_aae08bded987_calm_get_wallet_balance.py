"""Prevent get_wallet_balance crashing"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "aae08bded987"
down_revision = "ecc93a7cd1a2"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.get_wallet_balance(user_id bigint, only_used_bookings boolean) RETURNS numeric
        LANGUAGE plpgsql
        AS $$
        DECLARE
            deposit_id bigint := (SELECT deposit.id FROM deposit WHERE "userId" = user_id AND "expirationDate" > now() ORDER BY "expirationDate" DESC LIMIT 1);
        BEGIN
            RETURN
                CASE WHEN deposit_id IS NOT NULL THEN get_deposit_balance(deposit_id, only_used_bookings) ELSE 0 END;
        END;
        $$;
        ;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.get_wallet_balance(user_id bigint, only_used_bookings boolean) RETURNS numeric
        LANGUAGE plpgsql
        AS $$
        DECLARE
            deposit_id bigint := (SELECT deposit.id FROM deposit WHERE "userId" = user_id AND "expirationDate" > now());
        BEGIN
            RETURN
                CASE WHEN deposit_id IS NOT NULL THEN get_deposit_balance(deposit_id, only_used_bookings) ELSE 0 END;
        END;
        $$;
        ;
        """
    )
