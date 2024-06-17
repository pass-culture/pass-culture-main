"""Drop offer_music_sub_type_idx index
"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "49b4f3ce3751"
down_revision = "8698fb928069"


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index("offer_music_sub_type_idx", table_name="offer", if_exists=True, postgresql_concurrently=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("""SET SESSION statement_timeout = '2600s'""")
        op.execute(
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS
      offer_music_sub_type_idx ON public.offer USING btree (("jsonData" ->> 'musicSubType'))
      WHERE (("jsonData" -> 'musicSubType')) IS NOT NULL;
    """
        )
        op.execute(
            f"""
              SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
          """
        )
    # ### end Alembic commands ###
