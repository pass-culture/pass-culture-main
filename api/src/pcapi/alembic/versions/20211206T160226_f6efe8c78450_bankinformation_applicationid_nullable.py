"""BankInformation_applicationId_nullable
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f6efe8c78450"
down_revision = "d8d88115998e"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("bank_information", "applicationId", existing_type=sa.INTEGER(), nullable=True)


def downgrade():
    op.alter_column("bank_information", "applicationId", existing_type=sa.INTEGER(), nullable=False)
