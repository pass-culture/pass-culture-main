"""Add wishlists and wishlist items."""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
revision = "5e1c0a9d7b32"
down_revision = "73d81fa4c05b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "wishlist",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("visibility", sa.Text(), nullable=False, server_default="private"),
        sa.Column("share_token", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("share_token", name="wishlist_share_token_key"),
        sa.CheckConstraint("visibility IN ('private', 'unlisted', 'public')", name="check_wishlist_visibility"),
        sa.CheckConstraint("char_length(btrim(name)) BETWEEN 1 AND 100", name="check_wishlist_name_length"),
    )
    op.create_index("ix_wishlist_user_id", "wishlist", ["user_id"])
    op.create_table(
        "wishlist_item",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("wishlist_id", sa.BigInteger(), sa.ForeignKey("wishlist.id", ondelete="CASCADE"), nullable=False),
        sa.Column("work_id", sa.BigInteger(), sa.ForeignKey("work.id", ondelete="CASCADE"), nullable=True),
        sa.Column("artist_id", sa.Text(), sa.ForeignKey("artist.id", ondelete="CASCADE"), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "(work_id IS NOT NULL) != (artist_id IS NOT NULL)", name="check_wishlist_item_exactly_one_target"
        ),
    )
    for column in ("wishlist_id", "work_id", "artist_id"):
        op.create_index(f"ix_wishlist_item_{column}", "wishlist_item", [column])
    op.create_index(
        "ix_unique_wishlist_item_work",
        "wishlist_item",
        ["wishlist_id", "work_id"],
        unique=True,
        postgresql_where=sa.text("work_id IS NOT NULL"),
    )
    op.create_index(
        "ix_unique_wishlist_item_artist",
        "wishlist_item",
        ["wishlist_id", "artist_id"],
        unique=True,
        postgresql_where=sa.text("artist_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_table("wishlist_item")
    op.drop_table("wishlist")
