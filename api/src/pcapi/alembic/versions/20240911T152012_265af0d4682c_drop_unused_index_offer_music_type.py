"""Drop unused index on offer.jsonData['musicType']"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "265af0d4682c"
down_revision = "60adfaea930c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.drop_index(
            "offer_music_type_idx",
            table_name="offer",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.execute(
            """
                CREATE INDEX CONCURRENTLY IF NOT EXISTS
                offer_music_type_idx ON public.offer USING btree (("jsonData" ->> 'musicType'::text))
                WHERE (("jsonData" ->> 'musicType'::text)) IS NOT NULL;
            """
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
