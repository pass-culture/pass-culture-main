"""Make collective offer's contact email nullable"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "374e35815645"
down_revision = "4ff6cb80daee"
branch_labels: tuple | None = None
depends_on: tuple | None = None


def upgrade() -> None:
    op.alter_column("collective_offer", "contactEmail", existing_type=sa.VARCHAR(length=120), nullable=True)


def downgrade() -> None:
    op.alter_column("collective_offer", "contactEmail", existing_type=sa.VARCHAR(length=120), nullable=False)
