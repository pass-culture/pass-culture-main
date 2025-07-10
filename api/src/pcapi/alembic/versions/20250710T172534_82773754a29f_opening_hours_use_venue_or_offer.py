"""opening hours: use venue or offer"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "82773754a29f"
down_revision = "1c971d27bcb9"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("opening_hours", "venueId", existing_type=sa.BIGINT(), nullable=True)
    op.add_column("opening_hours", sa.Column("offerId", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "opening_hours_offerId_fkey",
        "opening_hours",
        "offer",
        ["offerId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )

    op.execute(
        """
        ALTER TABLE "opening_hours"
        ADD CONSTRAINT "opening_hours_uses_either_venue_or_offer"
        CHECK (
            ("venueId" IS NULL AND "offerId" IS NOT NULL)
            OR ("venueId" IS NOT NULL AND "offerId" IS NULL)
        )
        NOT VALID
        """
    )


def downgrade() -> None:
    op.drop_constraint("opening_hours_uses_either_venue_or_offer", "opening_hours")
    op.drop_column("opening_hours", "offerId")
