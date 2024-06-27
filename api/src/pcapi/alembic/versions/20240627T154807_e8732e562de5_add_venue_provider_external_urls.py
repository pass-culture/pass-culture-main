"""
Add `venue_provider_external_urls` table
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "e8732e562de5"
down_revision = "e92c101b449f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "venue_provider_external_urls",
        sa.Column("isActive", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("venueProviderId", sa.BigInteger(), nullable=False),
        sa.Column("bookingExternalUrl", sa.Text(), nullable=True),
        sa.Column("cancelExternalUrl", sa.Text(), nullable=True),
        sa.Column("notificationExternalUrl", sa.Text(), nullable=True),
        sa.CheckConstraint(
            '"bookingExternalUrl" IS NOT NULL OR "notificationExternalUrl" IS NOT NULL',
            name="check_at_least_one_of_the_external_url_is_set",
        ),
        sa.CheckConstraint(
            '("bookingExternalUrl" IS NOT NULL AND "cancelExternalUrl" IS NOT NULL) OR ("bookingExternalUrl" IS NULL AND "cancelExternalUrl" IS NULL)',
            name="check_ticketing_external_urls_both_set_or_null",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("venueProviderId"),
    )


def downgrade() -> None:
    op.drop_table("venue_provider_external_urls")
