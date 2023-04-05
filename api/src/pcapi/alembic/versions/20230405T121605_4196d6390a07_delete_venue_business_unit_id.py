"""Delete venue.businessUnitId"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4196d6390a07"
down_revision = "4d03be4b49ae"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("venue", "businessUnitId")


def downgrade() -> None:
    op.add_column("venue", sa.Column("businessUnitId", sa.INTEGER(), autoincrement=False, nullable=True))
