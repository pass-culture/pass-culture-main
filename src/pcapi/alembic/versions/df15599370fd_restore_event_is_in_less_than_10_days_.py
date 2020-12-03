"""Restore event_is_in_less_than_10_days function

Revision ID: df15599370fd
Revises: 87eba0d86e80
Create Date: 2020-12-03 16:38:14.198175

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "df15599370fd"
down_revision = "87eba0d86e80"
branch_labels = None
depends_on = None


def upgrade():
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


def downgrade():
    op.execute("DROP FUNCTION event_is_in_less_than_10_days;")
