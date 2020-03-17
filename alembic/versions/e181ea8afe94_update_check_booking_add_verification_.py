"""update_check_booking_add_verification_on_beginning_datetime

Revision ID: e181ea8afe94
Revises: 2fb60c9897d3
Create Date: 2020-03-17 10:45:50.632755

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'e181ea8afe94'
down_revision = '2fb60c9897d3'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''
    CREATE OR REPLACE FUNCTION check_booking()
    RETURNS TRIGGER AS $$
    DECLARE
    lastStockUpdate date := (SELECT "dateModified" FROM stock WHERE id=NEW."stockId");
    BEGIN
    IF EXISTS (SELECT "available" FROM stock WHERE id=NEW."stockId" AND "available" IS NOT NULL)
    AND (
        (SELECT "available" FROM stock WHERE id=NEW."stockId") <
        (
            SELECT SUM(quantity)
    FROM booking
    WHERE "stockId"=NEW."stockId"
    AND (
        NOT "isCancelled" AND NOT "isUsed"
    OR ("isUsed" AND "dateUsed" > lastStockUpdate)
    )
    )
    ) THEN
    RAISE EXCEPTION 'tooManyBookings'
    USING HINT = 'Number of bookings cannot exceed "stock.available"';
    END IF;

    IF (SELECT get_wallet_balance(NEW."userId", false) < 0)
    THEN RAISE EXCEPTION 'insufficientFunds'
    USING HINT = 'The user does not have enough credit to book';
    END IF;

    IF EXISTS (SELECT "beginningDatetime" FROM stock WHERE id=NEW."stockId" AND "beginningDatetime" < NOW())
    THEN RAISE EXCEPTION 'beginningDateTimePassed'
    USING HINT = 'The beginning date time for this event has passed';
    END IF;

    RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    ''')


def downgrade():
    ('''
    CREATE OR REPLACE FUNCTION check_booking()
    RETURNS TRIGGER AS $$
    DECLARE
    lastStockUpdate date := (SELECT "dateModified" FROM stock WHERE id=NEW."stockId");
    BEGIN
    IF EXISTS (SELECT "available" FROM stock WHERE id=NEW."stockId" AND "available" IS NOT NULL)
    AND (
        (SELECT "available" FROM stock WHERE id=NEW."stockId") <
        (
            SELECT SUM(quantity)
    FROM booking
    WHERE "stockId"=NEW."stockId"
    AND (
        NOT "isCancelled" AND NOT "isUsed"
    OR ("isUsed" AND "dateUsed" > lastStockUpdate)
    )
    )
    ) THEN
    RAISE EXCEPTION 'tooManyBookings'
    USING HINT = 'Number of bookings cannot exceed "stock.available"';
    END IF;

    IF (SELECT get_wallet_balance(NEW."userId", false) < 0)
    THEN RAISE EXCEPTION 'insufficientFunds'
    USING HINT = 'The user does not have enough credit to book';
    END IF;

    RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    ''')
