"""add idPicturesStored column to beneficiary_fraud_check table
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "22873a9e00e1"
down_revision = "25666068cabb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("beneficiary_fraud_check", sa.Column("idPicturesStored", sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column("beneficiary_fraud_check", "idPicturesStored")
