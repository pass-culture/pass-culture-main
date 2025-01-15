"""drop offers music, show type and subtypes indexes"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ffc1d7402c8a"
down_revision = "43fee1eab19d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("offer_music_subcategory_with_gtl_id_substr_idx"),
            table_name="offer",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            op.f("offer_show_sub_type_idx"),
            table_name="offer",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            op.f("offer_show_type_idx"),
            table_name="offer",
            postgresql_concurrently=True,
            if_exists=True,
        )


def downgrade() -> None:
    # We s-wouldn't want to recreate the index. The features are currently unused
    pass
