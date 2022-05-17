"""Create cinema_provider_pivot_table
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f96e62709e85"
down_revision = "7c3f40e7f77a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cinema_provider_pivot",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("venueId", sa.BigInteger(), nullable=True),
        sa.Column("providerId", sa.BigInteger(), nullable=False),
        sa.Column("idAtProvider", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["providerId"],
            ["provider.id"],
        ),
        sa.ForeignKeyConstraint(
            ["venueId"],
            ["venue.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("venueId"),
        sa.UniqueConstraint("venueId", "providerId", name="unique_pivot_venue_provider"),
    )


def downgrade() -> None:
    op.drop_table("cinema_provider_pivot")
