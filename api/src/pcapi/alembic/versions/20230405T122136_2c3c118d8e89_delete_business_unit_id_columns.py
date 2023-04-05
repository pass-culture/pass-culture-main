"""Delete businessUnitId columns (+ pricing.siret)"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2c3c118d8e89"
down_revision = "4196d6390a07"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("cashflow", "businessUnitId")
    op.drop_column("invoice", "businessUnitId")
    op.drop_column("pricing", "siret")
    op.drop_column("pricing", "businessUnitId")


def downgrade() -> None:
    op.add_column("pricing", sa.Column("businessUnitId", sa.BIGINT(), autoincrement=False, nullable=True))
    op.add_column("pricing", sa.Column("siret", sa.VARCHAR(length=14), autoincrement=False, nullable=True))
    op.add_column("invoice", sa.Column("businessUnitId", sa.BIGINT(), autoincrement=False, nullable=True))
    op.add_column("cashflow", sa.Column("businessUnitId", sa.BIGINT(), autoincrement=False, nullable=True))
