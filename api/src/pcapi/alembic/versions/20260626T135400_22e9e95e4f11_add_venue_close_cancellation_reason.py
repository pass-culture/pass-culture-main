"""add VENUE_CLOSED booking cancellation reason"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "22e9e95e4f11"
down_revision = "5dc3a149e8fa"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE cancellation_reason ADD VALUE IF NOT EXISTS 'VENUE_CLOSED' AFTER 'OFFERER_CONNECT_AS';")
    op.execute(
        "ALTER TYPE bookingcancellationreasons ADD VALUE IF NOT EXISTS 'VENUE_CLOSED' AFTER 'OFFERER_CONNECT_AS';"
    )


def downgrade() -> None:
    pass
