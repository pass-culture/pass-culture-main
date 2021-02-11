"""Update `check_booking`

Revision ID: 514dfbeddddf
Revises: 0867450b4c30
Create Date: 2021-02-08 10:58:14.217608

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "514dfbeddddf"
down_revision = "0867450b4c30"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
    CREATE OR REPLACE FUNCTION get_wallet_balance(user_id BIGINT, only_used_bookings BOOLEAN)
    RETURNS NUMERIC(10,2) AS $$
    DECLARE
        sum_deposits NUMERIC ;
        sum_bookings NUMERIC ;
    BEGIN
        SELECT COALESCE(SUM(amount), 0)
        INTO sum_deposits
        FROM deposit
        WHERE "userId"=user_id
        AND ("expirationDate" > now() OR "expirationDate" IS NULL);

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
        """
    )


def downgrade():
    # No downgrade, since the previous version of the SQL function has a huge bug.
    pass
