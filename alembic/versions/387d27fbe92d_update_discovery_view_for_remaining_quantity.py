"""update_discovery_view_for_remaining_quantity

Revision ID: 387d27fbe92d
Revises: 48440c1d122a
Create Date: 2020-03-25 13:07:27.703029

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '387d27fbe92d'
down_revision = '48440c1d122a'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
            CREATE OR REPLACE FUNCTION offer_has_at_least_one_bookable_stock(offer_id BIGINT)
            RETURNS SETOF INTEGER AS
            $body$
            BEGIN
                RETURN QUERY
                SELECT 1
                    FROM stock
                    WHERE stock."offerId" = offer_id
                    AND stock."isSoftDeleted" = FALSE
                    AND (stock."beginningDatetime" > NOW()
                        OR stock."beginningDatetime" IS NULL)
                    AND (stock."bookingLimitDatetime" > NOW()
                        OR stock."bookingLimitDatetime" IS NULL)
                    AND (stock.available IS NULL
                        OR (SELECT greatest(stock.available - COALESCE(sum(booking.quantity), 0),0)
                                FROM booking
                                WHERE booking."stockId" = stock.id
                                AND booking."isCancelled" = FALSE
                            ) > 0
                        );
            END
            $body$
            LANGUAGE plpgsql;
        """)


def downgrade():
    op.execute("""
            CREATE OR REPLACE FUNCTION offer_has_at_least_one_bookable_stock(offer_id BIGINT)
            RETURNS SETOF INTEGER AS
            $body$
            BEGIN
                RETURN QUERY
                SELECT 1
                    FROM stock
                    WHERE stock."offerId" = offer_id
                    AND stock."isSoftDeleted" = FALSE
                    AND (stock."beginningDatetime" > NOW()
                        OR stock."beginningDatetime" IS NULL)
                    AND (stock."bookingLimitDatetime" > NOW()
                        OR stock."bookingLimitDatetime" IS NULL)
                    AND (stock.available IS NULL
                        OR (SELECT greatest(stock.available - COALESCE(sum(booking.quantity), 0),0)
                                FROM booking
                                WHERE booking."stockId" = stock.id
                                AND (booking."isUsed" = FALSE
                                        AND booking."isCancelled" = FALSE
                                        OR booking."isUsed" = TRUE
                                        AND booking."dateUsed" > stock."dateModified")
                            ) > 0
                        );
            END
            $body$
            LANGUAGE plpgsql;
        """)
