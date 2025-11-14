"""Create unique index: ix_unique_artist_wikidata_id"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3f2f6ae24d02"
down_revision = "eb6ac3ba2c6a"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")

        op.create_index(
            "ix_unique_artist_wikidata_id",
            "artist",
            ["wikidata_id"],
            unique=True,
            postgresql_concurrently=True,
            if_not_exists=True,
        )

        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_unique_artist_wikidata_id",
            table_name="artist",
            postgresql_concurrently=True,
            if_exists=True,
        )
