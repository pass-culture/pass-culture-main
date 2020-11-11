"""Rename venue name from Offre en ligne to Offre numerique

Revision ID: 6c67573ad14f
Revises: 16f46a506e91
Create Date: 2019-09-17 08:42:40.113535

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "6c67573ad14f"
down_revision = "16f46a506e91"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
            UPDATE venue 
            SET "name"=REPLACE("name", 'Offre en ligne', 'Offre numérique')
            WHERE "name" LIKE '%Offre en ligne%'; 
            """
    )


def downgrade():
    op.execute(
        """
            UPDATE venue 
            SET "name"=REPLACE("name", 'Offre numérique', 'Offre en ligne') 
            WHERE "name" LIKE '%Offre numérique%'; 
            """
    )
