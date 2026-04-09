"""Create index: ix_booking_venueId_dateCreated"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b69574766fe3"
down_revision = "edc44f1d889e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout=0")
        op.create_index(
            "ix_booking_venueId_dateCreated",
            "booking",
            ["venueId", "dateCreated"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_booking_venueId_dateCreated",
            table_name="booking",
            postgresql_concurrently=True,
            if_exists=True,
        )
