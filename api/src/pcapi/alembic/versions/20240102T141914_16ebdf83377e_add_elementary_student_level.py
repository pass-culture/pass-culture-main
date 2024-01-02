"""Add ECOLES_INNOVANTES_MARSEILLE_EN_GRAND_ELEMENTAIRE to student levels values"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "16ebdf83377e"
down_revision = "a10993ffc712"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TYPE studentlevels
        RENAME VALUE 'ECOLES_INNOVANTES_MARSEILLE_EN_GRAND_PRIMAIRE' TO 'ECOLES_INNOVANTES_MARSEILLE_EN_GRAND_ELEMENTAIRE';
    """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TYPE studentlevels
        RENAME VALUE 'ECOLES_INNOVANTES_MARSEILLE_EN_GRAND_ELEMENTAIRE' TO 'ECOLES_INNOVANTES_MARSEILLE_EN_GRAND_PRIMAIRE';
    """
    )
