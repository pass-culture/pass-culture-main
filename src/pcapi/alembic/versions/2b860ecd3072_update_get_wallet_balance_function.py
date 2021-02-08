"""Populate Deposit.expirationDate

Revision ID: 2b860ecd3072
Revises: 3bf0e437edb0
Create Date: 2021-02-08 10:58:14.217608

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "2b860ecd3072"
down_revision = "3bf0e437edb0"
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
        AND "expirationDate" > now() OR "expirationDate" IS NULL;

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

        RETURN GREATEST(0, (sum_deposits - sum_bookings));
    END; $$
    LANGUAGE plpgsql;
        """
    )


def downgrade():
    op.execute(
        """
    DROP FUNCTION IF EXISTS get_wallet_balance(user_id BIGINT);

    CREATE OR REPLACE FUNCTION get_wallet_balance(user_id BIGINT, only_used_bookings BOOLEAN)
    RETURNS NUMERIC(10,2) AS $$
    DECLARE
        sum_deposits NUMERIC ;
        sum_bookings NUMERIC ;
    BEGIN
        SELECT COALESCE(SUM(amount), 0)
        INTO sum_deposits
        FROM deposit
        WHERE "userId"=user_id;

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
