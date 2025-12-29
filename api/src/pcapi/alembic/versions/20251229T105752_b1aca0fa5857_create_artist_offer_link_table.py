"""Create artist_offer_link table"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings
from pcapi.core.artist.models import ArtistType
from pcapi.utils import db as db_utils


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b1aca0fa5857"
down_revision = "250129872250"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='45s'")
        op.execute("SET SESSION lock_timeout='10s'")
        op.create_table(
            "artist_offer_link",
            sa.Column("offer_id", sa.BigInteger(), nullable=False),
            sa.Column("artist_type", db_utils.MagicEnum(ArtistType), nullable=False),
            sa.Column("custom_name", sa.Text(), nullable=True),
            sa.Column("artist_id", sa.Text(), nullable=True),
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.ForeignKeyConstraint(["artist_id"], ["artist.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["offer_id"], ["offer.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("offer_id", "artist_type", "artist_id", name="unique_offer_artist_constraint"),
            sa.UniqueConstraint("offer_id", "artist_type", "custom_name", name="unique_offer_custom_artist_constraint"),
            sa.CheckConstraint(
                "(artist_id IS NOT NULL) OR (custom_name IS NOT NULL)", name="check_has_artist_or_custom_name"
            ),
            if_not_exists=True,
        )
        op.create_index(
            op.f("ix_artist_offer_link_artist_id"),
            "artist_offer_link",
            ["artist_id"],
            unique=False,
            if_not_exists=True,
            postgresql_concurrently=True,
        )
        op.create_index(
            op.f("ix_artist_offer_link_offer_id"),
            "artist_offer_link",
            ["offer_id"],
            unique=False,
            if_not_exists=True,
            postgresql_concurrently=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
        op.execute(f"SET SESSION lock_timeout={settings.DATABASE_LOCK_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION lock_timeout='10s'")
        op.execute("SET SESSION statement_timeout='45s'")
        op.drop_index(
            op.f("ix_artist_offer_link_offer_id"),
            table_name="artist_offer_link",
            if_exists=True,
            postgresql_concurrently=True,
        )
        op.drop_index(
            op.f("ix_artist_offer_link_artist_id"),
            table_name="artist_offer_link",
            if_exists=True,
            postgresql_concurrently=True,
        )
        op.drop_table("artist_offer_link", if_exists=True)
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
        op.execute(f"SET SESSION lock_timeout={settings.DATABASE_LOCK_TIMEOUT}")
