"""remove offer.idAtProviders column
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fafc5b6c2398"
down_revision = "a9cb91d93ea0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("offer", "idAtProviders")


def downgrade() -> None:
    op.add_column("offer", sa.Column("idAtProviders", sa.VARCHAR(length=70), autoincrement=False, nullable=True))
