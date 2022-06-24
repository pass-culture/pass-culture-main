"""[pre] Make `pricing.businessUunitId` and `siret` nullable."""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "80c915a0b453"
down_revision = "3a02357e17ba"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("pricing", "businessUnitId", existing_type=sa.BIGINT(), nullable=True)
    op.alter_column("pricing", "siret", existing_type=sa.VARCHAR(length=14), nullable=True)


def downgrade():
    op.alter_column("pricing", "siret", existing_type=sa.VARCHAR(length=14), nullable=False)
    op.alter_column("pricing", "businessUnitId", existing_type=sa.BIGINT(), nullable=False)
