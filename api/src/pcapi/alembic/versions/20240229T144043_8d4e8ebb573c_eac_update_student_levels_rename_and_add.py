"""
eac update student levels rename and add
"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "8d4e8ebb573c"
down_revision = "8ed029bd05a6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TYPE
            studentlevels
        RENAME VALUE
            'ECOLES_INNOVANTES_MARSEILLE_EN_GRAND_MATERNELLE'
        TO
            'ECOLES_MARSEILLE_MATERNELLE';

        ALTER TYPE
            studentlevels
        RENAME VALUE
            'ECOLES_INNOVANTES_MARSEILLE_EN_GRAND_ELEMENTAIRE'
        TO
            'ECOLES_MARSEILLE_CP_CE1_CE2';

        ALTER TYPE
            studentlevels
        ADD VALUE IF NOT EXISTS
            'ECOLES_MARSEILLE_CM1_CM2';
    """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TYPE
            studentlevels
        RENAME VALUE
            'ECOLES_MARSEILLE_MATERNELLE'
        TO
            'ECOLES_INNOVANTES_MARSEILLE_EN_GRAND_MATERNELLE';

        ALTER TYPE
            studentlevels
        RENAME VALUE
            'ECOLES_MARSEILLE_CP_CE1_CE2'
        TO
            'ECOLES_INNOVANTES_MARSEILLE_EN_GRAND_ELEMENTAIRE';
    """
    )
