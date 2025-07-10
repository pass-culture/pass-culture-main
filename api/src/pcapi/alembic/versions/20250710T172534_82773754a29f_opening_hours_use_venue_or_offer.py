"""opening hours: use venue or offer"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "82773754a29f"
down_revision = "185416119576"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("opening_hours", "venueId", existing_type=sa.BIGINT(), nullable=True)
    op.add_column("opening_hours", sa.Column("offerId", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_opening_hours_offerId"), "opening_hours", ["offerId"], unique=False)
    op.create_foreign_key(None, "opening_hours", "offer", ["offerId"], ["id"], ondelete="CASCADE")

    op.execute(
        """
        ALTER TABLE "opening_hours"
        ADD CONSTRAINT "opening_hours_uses_either_venue_or_offer"
        CHECK (
            ("venueId" IS NULL AND "offerId" IS NOT NULL)
            OR ("venueId" IS NOT NULL AND "offerId" IS NULL)
        )
        """
    )

    op.execute(
        """
        ALTER TABLE "opening_hours"
        ADD CONSTRAINT "opening_hours_unique_object_weekday_timespan"
        UNIQUE ("venueId", "offerId", "weekday", "timespan")
        """
    )


def downgrade() -> None:
    op.drop_constraint("opening_hours_unique_object_weekday_timespan", "opening_hours")
    op.drop_constraint("opening_hours_uses_either_venue_or_offer", "opening_hours")
    op.drop_index(op.f("ix_opening_hours_offerId"), table_name="opening_hours")
    op.drop_column("opening_hours", "offerId")
    op.alter_column("opening_hours", "venueId", existing_type=sa.BIGINT(), nullable=False)
