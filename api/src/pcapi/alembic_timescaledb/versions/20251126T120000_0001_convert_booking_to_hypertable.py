"""Convert booking table to TimescaleDB hypertable partitioned by dateCreated."""

from alembic import op


revision = "0001"
down_revision = None  # type: ignore[var-annotated]
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("""
        DO $$
        DECLARE
            is_hypertable BOOLEAN;
        BEGIN
            SELECT EXISTS (
                SELECT 1 FROM timescaledb_information.hypertables
                WHERE hypertable_name = 'booking'
            ) INTO is_hypertable;

            IF NOT is_hypertable THEN
                ALTER TABLE booking DROP CONSTRAINT IF EXISTS booking_pkey CASCADE;
                ALTER TABLE booking DROP CONSTRAINT IF EXISTS booking_token_key CASCADE;

                PERFORM create_hypertable(
                    'booking',
                    by_range('dateCreated'),
                    migrate_data => true,
                    if_not_exists => true
                );
            END IF;

            CREATE INDEX IF NOT EXISTS idx_booking_date_created
                ON booking ("dateCreated" DESC);
            CREATE INDEX IF NOT EXISTS idx_booking_offerer_date
                ON booking ("offererId", "dateCreated" DESC);
            CREATE INDEX IF NOT EXISTS idx_booking_venue_date
                ON booking ("venueId", "dateCreated" DESC);
            CREATE INDEX IF NOT EXISTS idx_booking_status_date
                ON booking (status, "dateCreated" DESC);
            CREATE INDEX IF NOT EXISTS idx_booking_token
                ON booking (token);
        END
        $$;
    """)


def downgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            RAISE EXCEPTION 'Hypertable conversion cannot be automatically reverted.';
        END
        $$;
    """)
