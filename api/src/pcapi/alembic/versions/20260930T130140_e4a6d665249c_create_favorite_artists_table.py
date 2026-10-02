"""Create favorite artists table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "e4a6d665249c"
down_revision = "c8cbc38c2bad"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "favorite_artist",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.Column("artistId", sa.Text(), nullable=False),
        sa.Column("dateCreated", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["artistId"], ["artist.id"]),
        sa.ForeignKeyConstraint(["userId"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("userId", "artistId", name="unique_user_artist_favorite"),
    )


def downgrade() -> None:
    op.drop_table("favorite_artist", if_exists=True)
