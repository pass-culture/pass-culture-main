"""
Add partial index for showSubType in Offer.extraData
"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "fadf7f6f4c60"
down_revision = "cb8859f6ac97"
branch_labels: tuple[str] | None = None
depends_on: tuple[str] | None = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute("""SET SESSION statement_timeout = '2600s'""")
    op.execute(
        """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            offer_show_sub_type_idx ON public.offer USING btree (("jsonData" ->> 'showSubType'::text))
            WHERE (("jsonData" ->> 'showSubType'::text)) IS NOT NULL;
        """
    )
    op.execute(
        f"""
            SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
        """
    )


def downgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")  # helm upgrade timeout
    op.drop_index("offer_show_sub_type_idx", table_name="offer", if_exists=True)
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
