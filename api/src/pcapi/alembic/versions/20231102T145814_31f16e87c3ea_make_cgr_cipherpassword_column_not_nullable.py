"""
Make CGR `encryptedPassword` non nullable
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "31f16e87c3ea"
down_revision = "ad78bc82b4fb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("cgr_cinema_details", "encryptedPassword", existing_type=sa.TEXT(), nullable=False)


def downgrade() -> None:
    op.alter_column("cgr_cinema_details", "encryptedPassword", existing_type=sa.TEXT(), nullable=True)
