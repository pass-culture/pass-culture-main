"""add artist_music_platform table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d4e5f6a7b8c9"
down_revision = "22e9e95e4f11"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "artist_music_platform",
        sa.Column("id", sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column(
            "artist_id",
            sa.Text(),
            sa.ForeignKey("artist.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("spotify_id", sa.Text(), nullable=True),
        sa.Column("isni_id", sa.Text(), nullable=True),
        sa.Column("apple_music_id", sa.Text(), nullable=True),
        sa.Column("deezer_id", sa.Text(), nullable=True),
        sa.Column("genius_id", sa.Text(), nullable=True),
        sa.Column("soundcloud_id", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("artist_music_platform", if_exists=True)
