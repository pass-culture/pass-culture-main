"""Add work and artist targets to favorites."""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
revision = "7e4a2b9c610d"
down_revision = "5e1c0a9d7b32"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("favorite", sa.Column("work_id", sa.BigInteger(), nullable=True))
    op.add_column("favorite", sa.Column("artist_id", sa.Text(), nullable=True))
    op.add_column("favorite", sa.Column("offer_origin_id", sa.BigInteger(), nullable=True))
    for column, target in (("work_id", "work"), ("artist_id", "artist"), ("offer_origin_id", "offer")):
        op.create_foreign_key(
            f"favorite_{column}_fkey",
            "favorite",
            target,
            [column],
            ["id"],
            ondelete="SET NULL" if column == "offer_origin_id" else None,
            postgresql_not_valid=True,
        )
    op.create_check_constraint(
        "favorite_exactly_one_target",
        "favorite",
        'num_nonnulls("offerId", work_id, artist_id) = 1',
        postgresql_not_valid=True,
    )
    op.create_check_constraint(
        "favorite_origin_requires_work",
        "favorite",
        "offer_origin_id IS NULL OR work_id IS NOT NULL",
        postgresql_not_valid=True,
    )
    op.alter_column("favorite", "offerId", existing_type=sa.BigInteger(), nullable=True)
    op.execute('UPDATE favorite SET "dateCreated" = timezone(\'UTC\', now()) WHERE "dateCreated" IS NULL')
    op.create_check_constraint(
        "favorite_date_created_not_null", "favorite", '"dateCreated" IS NOT NULL', postgresql_not_valid=True
    )
    with op.get_context().autocommit_block():
        for column in ("work_id", "artist_id", "offer_origin_id"):
            op.create_index(
                f"ix_favorite_{column}", "favorite", [column], postgresql_concurrently=True, if_not_exists=True
            )
        for column, suffix in (("offerId", "offer"), ("work_id", "work"), ("artist_id", "artist")):
            op.create_index(
                f"ix_unique_favorite_{suffix}",
                "favorite",
                ["userId", column],
                unique=True,
                postgresql_where=sa.column(column).is_not(None),
                postgresql_concurrently=True,
                if_not_exists=True,
            )


def downgrade() -> None:
    op.execute(
        "DO $$ BEGIN IF EXISTS (SELECT 1 FROM favorite WHERE work_id IS NOT NULL OR artist_id IS NOT NULL) "
        "THEN RAISE EXCEPTION 'Cannot downgrade while cultural favorites exist'; END IF; END $$"
    )
    for name in ("favorite_date_created_not_null", "favorite_origin_requires_work", "favorite_exactly_one_target"):
        op.drop_constraint(name, "favorite", type_="check")
    op.alter_column("favorite", "offerId", existing_type=sa.BigInteger(), nullable=False)
    with op.get_context().autocommit_block():
        for suffix in ("offer", "work", "artist"):
            op.drop_index(
                f"ix_unique_favorite_{suffix}", table_name="favorite", postgresql_concurrently=True, if_exists=True
            )
    for column in ("offer_origin_id", "artist_id", "work_id"):
        op.drop_column("favorite", column)
