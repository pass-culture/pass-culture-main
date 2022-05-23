"""remove allocine_pivot siret
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bdfc48c090db"
down_revision = "17640cc03876"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("allocine_pivot", "siret")


def downgrade() -> None:
    op.add_column("allocine_pivot", sa.Column("siret", sa.VARCHAR(length=14), autoincrement=False, nullable=True))
