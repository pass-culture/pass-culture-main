"""postal_code_and_phone_number_educational_institution_not_nullable
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "76d1434f787d"
down_revision = "2967ed08d3e0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("educational_institution", "postalCode", existing_type=sa.VARCHAR(length=10), nullable=False)
    op.alter_column("educational_institution", "phoneNumber", existing_type=sa.VARCHAR(length=30), nullable=False)


def downgrade() -> None:
    op.alter_column("educational_institution", "phoneNumber", existing_type=sa.VARCHAR(length=30), nullable=True)
    op.alter_column("educational_institution", "postalCode", existing_type=sa.VARCHAR(length=10), nullable=True)
