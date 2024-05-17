"""create index for 2 first characters of offer gtl id
"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8698fb928069"
down_revision = "e6c2d152ff40"


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("""SET SESSION statement_timeout = '2600s'""")
        op.execute(
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS
      offer_substr_gtl_id_idx ON public.offer USING btree ((substr("jsonData" ->> 'gtl_id', 1, 2)))
      WHERE (("jsonData" -> 'gtl_id')) IS NOT NULL;
    """
        )
        op.execute(
            f"""
              SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
          """
        )
    # ### end Alembic commands ###


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index("offer_substr_gtl_id_idx", table_name="offer", if_exists=True, postgresql_concurrently=True)
    # ### end Alembic commands ###
