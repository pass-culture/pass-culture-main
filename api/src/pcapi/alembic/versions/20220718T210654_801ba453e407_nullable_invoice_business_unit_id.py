"""Make invoice.businessUnitId nullable."""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "801ba453e407"
down_revision = "58102ed26597"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("invoice", "businessUnitId", existing_type=sa.BIGINT(), nullable=True)


def downgrade():
    op.alter_column("invoice", "businessUnitId", existing_type=sa.BIGINT(), nullable=False)
