"""create google places info table and link it to venue
the table contains the place_id at google, the banner url
and the banner meta data.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "a10993ffc712"
down_revision = "ec0f52ada8fa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "google_places_info",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("venueId", sa.BigInteger(), nullable=False),
        sa.Column("placeId", sa.Text(), nullable=False),
        sa.Column("bannerUrl", sa.Text(), nullable=True),
        sa.Column("bannerMeta", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(["venueId"], ["venue.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("placeId"),
    )
    op.create_index(op.f("ix_google_places_info_venueId"), "google_places_info", ["venueId"], unique=True)


def downgrade() -> None:
    op.drop_table("google_places_info")
