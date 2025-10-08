"""Add achievements FK constraints"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "53e2600b8585"
down_revision = "1007ef88d004"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_foreign_key(
        "achievement_userId_fkey",
        "achievement",
        "user",
        ["userId"],
        ["id"],
        postgresql_not_valid=True,
    )

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
        op.add_column("achievement", sa.Column("bookingDateCreated", sa.DateTime(), nullable=True))
        op.execute("""
            UPDATE achievement a
            SET "bookingDateCreated" = b."dateCreated"
            FROM booking b
            WHERE a."bookingId" = b.id;
        """)
        op.create_foreign_key(
            "achievement_bookingId_fkey",
            "achievement",
            "booking",
            ["bookingId", "bookingDateCreated"],
            ["id", "dateCreated"],
            postgresql_not_valid=True,
        )
    else:
        op.create_foreign_key(
            "achievement_bookingId_fkey",
            "achievement",
            "booking",
            ["bookingId"],
            ["id"],
            postgresql_not_valid=True,
        )

    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_achievement_userId"),
            "achievement",
            ["userId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


# TODO (igabriele, 2025-10-08): Check the downgrade logic (unfinished).
def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_achievement_userId"),
            table_name="achievement",
            postgresql_concurrently=True,
            if_exists=True,
        )
