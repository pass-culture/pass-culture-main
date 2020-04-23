"""add_type_to_venue

Revision ID: edb77d0140b7
Revises: 040875ff5d5b
Create Date: 2020-04-20 13:57:01.460387

"""
import sqlalchemy as sa
from sqlalchemy import ForeignKey
from alembic import op

revision = 'edb77d0140b7'
down_revision = '040875ff5d5b'
branch_labels = None
depends_on = None


def upgrade():
    venue_type_table = op.create_table(
        'venue_type',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('label', sa.VARCHAR(100), nullable=False),
    )

    op.add_column('venue',
                  sa.Column('venueTypeId', sa.Integer, ForeignKey('venue_type.id'), nullable=True)
                  )

    op.bulk_insert(venue_type_table,
                   [
                       {'label': "Arts visuels, arts plastiques et galeries"},
                       {'label': "Centre culturel"},
                       {'label': "Cours et pratique artistiques"},
                       {'label': "Culture scientifique"},
                       {'label': "Festival"},
                       {'label': "Jeux / Jeux vidéos"},
                       {'label': "Librairie"},
                       {'label': "Bibliothèque ou médiathèque"},
                       {'label': "Musée"},
                       {'label': "Musique - Disquaire"},
                       {'label': "Musique - Magasin d’instruments"},
                       {'label': "Musique - Salle de concerts"},
                       {'label': "Offre numérique"},
                       {'label': "Patrimoine et tourisme"},
                       {'label': "Cinéma - Salle de projections"},
                       {'label': "Spectacle vivant"},
                       {'label': "Autre"}
                   ]
                   )


def downgrade():
    op.drop_column('venue', 'venueTypeId')
    op.drop_table('venue_type')
