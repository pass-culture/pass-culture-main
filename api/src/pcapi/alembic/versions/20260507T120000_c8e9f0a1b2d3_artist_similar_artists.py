"""Add artist similar-artists table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "c8e9f0a1b2d3"
down_revision = "f37686c3d4ed"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "artist_similar_artist",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("artist_id", sa.Text(), nullable=False),
        sa.Column("similar_artist_id", sa.Text(), nullable=False),
        sa.Column("similarity_rank", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["artist_id"], ["artist.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["similar_artist_id"], ["artist.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("artist_id", "similar_artist_id", name="uq_artist_similar_artist_pair"),
        sa.UniqueConstraint("artist_id", "similarity_rank", name="uq_artist_similar_artist_rank"),
        sa.CheckConstraint(
            "artist_id <> similar_artist_id",
            name="check_artist_similar_artist_not_self",
        ),
    )


def downgrade() -> None:
    op.drop_table("artist_similar_artist")
