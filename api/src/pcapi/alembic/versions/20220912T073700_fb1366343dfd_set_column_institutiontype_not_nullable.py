"""set_column_institutionType_not_nullable
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "fb1366343dfd"
down_revision = "3c4183de2005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("educational_institution", "institutionType", existing_type=sa.VARCHAR(length=80), nullable=False)


def downgrade() -> None:
    op.alter_column("educational_institution", "institutionType", existing_type=sa.VARCHAR(length=80), nullable=True)
