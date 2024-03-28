"""Add index on offer jsonData gtl_id for music categories
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "174265dad10d"
down_revision = "374e35815645"


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            offer_gtl_music_type_idx ON public.offer USING hash (("jsonData" ->> 'gtl_id'))
            WHERE "subcategoryId" in ('ABO_CONCERT', 'ABO_PLATEFORME_MUSIQUE', 'CAPTATION_MUSIQUE',
            'CONCERT', 'EVENEMENT_MUSIQUE', 'FESTIVAL_MUSIQUE', 'LIVESTREAM_MUSIQUE',
            'SUPPORT_PHYSIQUE_MUSIQUE_CD', 'SUPPORT_PHYSIQUE_MUSIQUE_VINYLE', 'TELECHARGEMENT_MUSIQUE');
        """
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(
            """
            DROP INDEX CONCURRENTLY IF EXISTS offer_ean_idx;
        """
        )
