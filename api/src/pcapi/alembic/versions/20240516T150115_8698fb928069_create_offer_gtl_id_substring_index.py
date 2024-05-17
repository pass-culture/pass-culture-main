"""create index for 2 first characters of offer gtl id
"""

from alembic import op

from pcapi import settings
from pcapi.core.categories.subcategories_v2 import MUSIC_TITELIVE_SUBCATEGORY_SEARCH_IDS


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8698fb928069"
down_revision = "2144f7e4df3c"


def upgrade() -> None:
    with op.get_context().autocommit_block():

        op.execute("""SET SESSION statement_timeout = '2600s'""")
        op.execute(
            f"""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            "offer_music_subcategory_with_gtl_id_substr_idx" 
            ON public.offer USING btree (
            "subcategoryId", 
            (substr("jsonData" ->> 'gtl_id'::text, 1, 2))
            ) 
            WHERE ("jsonData" ->> 'gtl_id') IS NOT NULL AND offer."subcategoryId" IN 
            ({", ".join([f"'{subcategory_id}'" for subcategory_id in MUSIC_TITELIVE_SUBCATEGORY_SEARCH_IDS])});
                    
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
        op.drop_index(
            "offer_music_subcategory_with_gtl_id_substr_idx",
            table_name="offer",
            if_exists=True,
            postgresql_concurrently=True,
        )
    # ### end Alembic commands ###
