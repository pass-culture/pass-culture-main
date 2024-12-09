"""
Add partial index for showType in Offer.extraData
"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "cb8859f6ac97"
down_revision = "c95cbcd8d765"
branch_labels: tuple[str] | None = None
depends_on: tuple[str] | None = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute("""SET SESSION statement_timeout = '2600s'""")
    op.execute(
        """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            offer_show_type_idx ON public.offer USING btree (("jsonData" ->> 'showType'::text))
            WHERE (("jsonData" ->> 'showType'::text)) IS NOT NULL;
        """
    )
    op.execute(
        f"""
            SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
        """
    )


def downgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")  # helm upgrade timeout
    op.drop_index("offer_show_type_idx", table_name="offer", if_exists=True)
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
