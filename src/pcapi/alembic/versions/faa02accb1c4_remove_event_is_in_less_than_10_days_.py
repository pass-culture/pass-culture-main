"""Remove event_is_in_less_than_10_days SQL function, formerly used
for recommendations.

Revision ID: faa02accb1c4
Revises: 7ba915ba9964
Create Date: 2020-11-26 14:39:25.308160

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "faa02accb1c4"
down_revision = "7ba915ba9964"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP FUNCTION event_is_in_less_than_10_days;")


def downgrade():
    op.execute(
        """
        CREATE OR REPLACE FUNCTION event_is_in_less_than_10_days(offer_id BIGINT)
        RETURNS SETOF INTEGER AS
        $body$
        BEGIN
           RETURN QUERY
           SELECT 1
            FROM stock
            WHERE stock."offerId" = offer_id
              AND (stock."beginningDatetime" IS NULL
                    OR stock."beginningDatetime" > NOW()
                   AND stock."beginningDatetime" < NOW() + INTERVAL '10 DAY');
        END
        $body$
        LANGUAGE plpgsql;
        """
    )
