"""Create favorite artists indexes"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "782c052e7408"
down_revision = "869c61cd3a23"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_favorite_artist_artistId"),
            "favorite_artist",
            ["artistId"],
            postgresql_concurrently=True,
            unique=False,
            if_not_exists=True,
        )
        op.create_index(
            op.f("ix_favorite_artist_userId"),
            "favorite_artist",
            ["userId"],
            postgresql_concurrently=True,
            unique=False,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_favorite_artist_userId"),
            table_name="favorite_artist",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            op.f("ix_favorite_artist_artistId"),
            table_name="favorite_artist",
            postgresql_concurrently=True,
            if_exists=True,
        )
