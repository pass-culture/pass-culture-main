"""Create favorite venues indexes"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2bc5d29e2492"
down_revision = "782c052e7408"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_favorite_venue_venueId"),
            "favorite_venue",
            ["venueId"],
            postgresql_concurrently=True,
            unique=False,
            if_not_exists=True,
        )
        op.create_index(
            op.f("ix_favorite_venue_userId"),
            "favorite_venue",
            ["userId"],
            postgresql_concurrently=True,
            unique=False,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_favorite_venue_userId"),
            table_name="favorite_venue",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            op.f("ix_favorite_venue_venueId"),
            table_name="favorite_venue",
            postgresql_concurrently=True,
            if_exists=True,
        )
