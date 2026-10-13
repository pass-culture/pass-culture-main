"""Add works, work artists and cultural discoveries."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
revision = "f4d92c76ab81"
down_revision = "c8cbc38c2bad"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "work",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("media_type", sa.Text(), nullable=False),
        sa.Column("release_year", sa.BigInteger(), nullable=True),
        sa.Column("visual_url", sa.String(), nullable=True),
        sa.Column("external_ids", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.CheckConstraint(
            "media_type IN ('book', 'film', 'music', 'performing_art', 'visual_art', 'video_game', 'other')",
            name="work_media_type",
        ),
    )
    op.create_table(
        "work_artist",
        sa.Column("work_id", sa.BigInteger(), sa.ForeignKey("work.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("artist_id", sa.Text(), sa.ForeignKey("artist.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role", sa.String(), nullable=False),
    )
    op.create_index("ix_work_artist_artist_id", "work_artist", ["artist_id"])
    op.create_table(
        "discovery",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("work_id", sa.BigInteger(), sa.ForeignKey("work.id"), nullable=True),
        sa.Column("artist_id", sa.Text(), sa.ForeignKey("artist.id"), nullable=True),
        sa.Column("offer_origin_id", sa.BigInteger(), sa.ForeignKey("offer.id", ondelete="SET NULL"), nullable=True),
        sa.Column("discovery_date", sa.Date(), nullable=False, server_default=sa.func.current_date()),
        sa.Column("format_context", sa.String(), nullable=True),
        sa.Column("sentiment", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "(work_id IS NOT NULL) != (artist_id IS NOT NULL)", name="check_discovery_exactly_one_target"
        ),
    )
    for column in ("user_id", "work_id", "artist_id", "offer_origin_id"):
        op.create_index(f"ix_discovery_{column}", "discovery", [column])
    op.add_column("artist", sa.Column("main_role", sa.String(), nullable=True))
    op.add_column("artist", sa.Column("external_ids", postgresql.JSONB(), nullable=True))
    op.add_column("product", sa.Column("work_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key("product_work_id_fkey", "product", "work", ["work_id"], ["id"], postgresql_not_valid=True)


def downgrade() -> None:
    op.drop_constraint("product_work_id_fkey", "product", type_="foreignkey")
    op.drop_column("product", "work_id")
    op.drop_column("artist", "external_ids")
    op.drop_column("artist", "main_role")
    op.drop_table("discovery")
    op.drop_table("work_artist")
    op.drop_table("work")
