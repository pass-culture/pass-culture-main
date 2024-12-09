"""
Add partial index for musicSubType in Offer.extraData
"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c95cbcd8d765"
down_revision = "36cf4c5380ad"
branch_labels: tuple[str] | None = None
depends_on: tuple[str] | None = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute("""SET SESSION statement_timeout = '2600s'""")
    op.execute(
        """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            offer_music_sub_type_idx ON public.offer USING btree (("jsonData" ->> 'musicSubType'::text))
            WHERE (("jsonData" ->> 'musicSubType'::text)) IS NOT NULL;
        """
    )
    op.execute(
        f"""
            SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
        """
    )


def downgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")  # helm upgrade timeout
    op.drop_index("offer_music_sub_type_idx", table_name="offer", if_exists=True)
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
