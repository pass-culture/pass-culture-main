"""
Create tables artist, artist_alias and artist_product_link
"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.artist.models import ArtistType
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "f8588023c126"
down_revision = "2b4a02b0a8d5"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "artist",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image", sa.Text(), nullable=True),
        sa.Column("image_license", sa.Text(), nullable=True),
        sa.Column("image_license_url", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_artist_name"), "artist", ["name"], unique=False)
    op.create_table(
        "artist_alias",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("artist_id", sa.Text(), nullable=False),
        sa.Column("artist_alias_name", sa.Text(), nullable=True),
        sa.Column("artist_cluster_id", sa.Text(), nullable=True),
        sa.Column("artist_type", MagicEnum(ArtistType), nullable=True),
        sa.Column("artist_wiki_data_id", sa.Text(), nullable=True),
        sa.Column("offer_category_id", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["artist_id"],
            ["artist.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_artist_alias_artist_id"), "artist_alias", ["artist_id"], unique=False)
    op.create_table(
        "artist_product_link",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("artist_id", sa.Text(), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("artist_type", MagicEnum(ArtistType), nullable=True),
        sa.ForeignKeyConstraint(["artist_id"], ["artist.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["product.id"], ondelete="CASCADE", postgresql_not_valid=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_artist_product_link_artist_id"), "artist_product_link", ["artist_id"], unique=False)
    op.create_index(op.f("ix_artist_product_link_product_id"), "artist_product_link", ["product_id"], unique=False)


def downgrade() -> None:
    op.drop_table("artist_product_link")
    op.drop_table("artist_alias")
    op.drop_table("artist")
