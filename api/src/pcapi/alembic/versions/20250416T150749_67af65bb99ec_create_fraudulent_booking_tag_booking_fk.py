"""Create FraudulentBookingTag booking foreign key constraint"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "67af65bb99ec"
down_revision = "b4eb9ea33b3e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    is_timescaledb_installed = conn.execute(
        sa.text("""
            SELECT EXISTS (
                SELECT 1 FROM pg_extension WHERE extname = 'timescaledb'
            );
        """)
    ).scalar()
    is_hypertable = False
    if is_timescaledb_installed:
        is_hypertable = conn.execute(
            sa.text("""
            SELECT EXISTS (
                SELECT 1 FROM timescaledb_information.hypertables
                WHERE hypertable_name = 'booking'
            );
        """)
        ).scalar()
    if is_hypertable:
        op.add_column("fraudulent_booking_tag", sa.Column("bookingDateCreated", sa.DateTime(), nullable=True))
        op.execute("""
            UPDATE fraudulent_booking_tag fbt
            SET "bookingDateCreated" = b."dateCreated"
            FROM booking b
            WHERE fbt."bookingId" = b.id;
        """)
        op.create_foreign_key(
            "fraudulent_booking_tag_booking_fk",
            "fraudulent_booking_tag",
            "booking",
            ["bookingId", "bookingDateCreated"],
            ["id", "dateCreated"],
            postgresql_not_valid=True,
        )
    else:
        op.create_foreign_key(
            "fraudulent_booking_tag_booking_fk",
            "fraudulent_booking_tag",
            "booking",
            ["bookingId"],
            ["id"],
            postgresql_not_valid=True,
        )


def downgrade() -> None:
    conn = op.get_bind()
    is_timescaledb_installed = conn.execute(
        sa.text("""
            SELECT EXISTS (
                SELECT 1 FROM pg_extension WHERE extname = 'timescaledb'
            );
        """)
    ).scalar()
    is_hypertable = False
    if is_timescaledb_installed:
        is_hypertable = conn.execute(
            sa.text("""
            SELECT EXISTS (
                SELECT 1 FROM timescaledb_information.hypertables
                WHERE hypertable_name = 'booking'
            );
        """)
        ).scalar()
    if is_hypertable:
        op.drop_constraint("fraudulent_booking_tag_booking_fk", "fraudulent_booking_tag", type_="foreignkey")
        op.drop_column("fraudulent_booking_tag", "bookingDateCreated")
    else:
        op.drop_constraint("fraudulent_booking_tag_booking_fk", "fraudulent_booking_tag", type_="foreignkey")
