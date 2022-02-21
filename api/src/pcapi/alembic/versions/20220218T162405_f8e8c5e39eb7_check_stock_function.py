"""Update `check_stock` SQL function."""
from alembic import op


# revision identifiers, used by Alembic.
revision = "f8e8c5e39eb7"
down_revision = "d3da2eac435d"
branch_labels = None
depends_on = None


OLD_DDL = """
    CREATE OR REPLACE FUNCTION check_stock()
    RETURNS TRIGGER AS $$
    BEGIN
      IF
       NOT NEW.quantity IS NULL
       AND
        (
         (
          SELECT SUM(booking.quantity)
          FROM booking
          WHERE "stockId"=NEW.id
          AND NOT booking.status = 'CANCELLED'
         ) > NEW.quantity
        )
      THEN
       RAISE EXCEPTION 'quantity_too_low'
       USING HINT = 'stock.quantity cannot be lower than number of bookings';
      END IF;

      IF NEW."bookingLimitDatetime" IS NOT NULL AND
        NEW."beginningDatetime" IS NOT NULL AND
         NEW."bookingLimitDatetime" > NEW."beginningDatetime" THEN

      RAISE EXCEPTION 'bookingLimitDatetime_too_late'
      USING HINT = 'bookingLimitDatetime after beginningDatetime';
      END IF;

      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
"""

NEW_DDL = """
    CREATE OR REPLACE FUNCTION check_stock()
    RETURNS TRIGGER AS $$
    BEGIN
      IF
       NOT NEW.quantity IS NULL
       -- We allow synchronized stocks to have a negative remaining quantity
       -- because items that have been booked through us could be sold
       -- by the library at the same time. In that case, we want to allow
       -- the update of `Stock.quantity` to reflect the reality.
       AND NEW."lastProviderId" IS NULL
       AND
        (
         (
          SELECT SUM(booking.quantity)
          FROM booking
          WHERE "stockId"=NEW.id
          AND NOT booking.status = 'CANCELLED'
         ) > NEW.quantity
        )
      THEN
       RAISE EXCEPTION 'quantity_too_low'
       USING HINT = 'stock.quantity cannot be lower than number of bookings';
      END IF;

      IF NEW."bookingLimitDatetime" IS NOT NULL AND
        NEW."beginningDatetime" IS NOT NULL AND
         NEW."bookingLimitDatetime" > NEW."beginningDatetime" THEN

      RAISE EXCEPTION 'bookingLimitDatetime_too_late'
      USING HINT = 'bookingLimitDatetime after beginningDatetime';
      END IF;

      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
"""


def upgrade():
    op.execute(NEW_DDL)


def downgrade():
    op.execute(OLD_DDL)
