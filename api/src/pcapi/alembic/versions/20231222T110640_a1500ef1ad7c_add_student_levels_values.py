"""add student levels values"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "a1500ef1ad7c"
down_revision = "64a8f6cecea6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TYPE studentlevels
        ADD VALUE IF NOT EXISTS 'ECOLES_INNOVANTES_MARSEILLE_EN_GRAND_MATERNELLE';

        ALTER TYPE studentlevels
        ADD VALUE IF NOT EXISTS 'ECOLES_INNOVANTES_MARSEILLE_EN_GRAND_PRIMAIRE';
    """
    )


def downgrade() -> None:
    # nothing to do: an enum value can't be removed
    pass
