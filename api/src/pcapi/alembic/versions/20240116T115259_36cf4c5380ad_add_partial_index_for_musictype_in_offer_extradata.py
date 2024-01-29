"""
Add partial index for musicType in Offer.extraData
"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "36cf4c5380ad"
down_revision = "3467ee234047"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute("""SET SESSION statement_timeout = '2600s'""")
    op.execute(
        """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            offer_music_type_idx ON public.offer USING btree (("jsonData" ->> 'musicType'::text))
            WHERE (("jsonData" ->> 'musicType'::text)) IS NOT NULL;
        """
    )
    op.execute(
        f"""
            SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
        """
    )


def downgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")  # helm upgrade timeout
    op.drop_index(
        "offer_music_type_idx",
        table_name="offer",
    )
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
