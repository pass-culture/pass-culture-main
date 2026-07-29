"""Drop artist_alias table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b3e1f2a4c5d6"
down_revision = "074c329a42a3"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_table("artist_alias")


def downgrade() -> None:
    op.create_table(
        "artist_alias",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("artist_id", sa.Text(), nullable=False),
        sa.Column("artist_alias_name", sa.Text(), nullable=True),
        sa.Column("artist_cluster_id", sa.Text(), nullable=True),
        sa.Column("artist_type", sa.Text(), nullable=True),
        sa.Column("artist_wiki_data_id", sa.Text(), nullable=True),
        sa.Column("offer_category_id", sa.Text(), nullable=True),
        sa.Column("date_created", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("date_modified", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["artist_id"], ["artist.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_artist_alias_artist_id", "artist_alias", ["artist_id"], unique=False)
    op.execute(
        "CREATE INDEX ix_artist_alias_trgm_unaccent_name ON artist_alias USING gin (immutable_unaccent(artist_alias_name) gin_trgm_ops)"
    )
