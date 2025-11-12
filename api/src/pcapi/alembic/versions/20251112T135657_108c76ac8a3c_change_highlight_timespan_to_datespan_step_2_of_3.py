"""Change highlight timespan to datespan step 2 of 3
Add data to daterange from timerange

INFO: The `DO $$ ...` block allow us to execute PL/pgSQL code.
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "108c76ac8a3c"
down_revision = "365ac49e50ae"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'highlight'
                      AND column_name = 'availability_timespan'
                      AND table_schema = 'public'
                ) THEN
                    UPDATE highlight
                    SET availability_datespan = daterange(
                        lower(availability_timespan)::date,
                        upper(availability_timespan)::date,
                        '[)'
                    );
                END IF;
            END $$;
            """
        )
    )

    op.execute(
        sa.text(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'highlight'
                      AND column_name = 'highlight_timespan'
                      AND table_schema = 'public'
                ) THEN
                    UPDATE highlight
                    SET highlight_datespan = daterange(
                        lower(highlight_timespan)::date,
                        upper(highlight_timespan)::date,
                        '[)'
                    );
                END IF;
            END $$;
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """UPDATE highlight SET availability_timespan = tsrange(
                (lower(availability_datespan)::date + time '00:00:00')::timestamp,
                (upper(availability_datespan)::date + time '00:00:00')::timestamp,
                '[)'
            );"""
        )
    )
    op.execute(
        sa.text(
            """UPDATE highlight SET highlight_timespan = tsrange(
                (lower(highlight_datespan)::date + time '00:00:00')::timestamp,
                (upper(highlight_datespan)::date + time '00:00:00')::timestamp,
                '[)'
            );"""
        )
    )
