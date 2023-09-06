"""Make password column not nullable in cgr_cinema_details table"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "eade6ec3120d"
down_revision = "e7f20c06dda4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("cgr_cinema_details", "password", existing_type=sa.TEXT(), nullable=False)


def downgrade() -> None:
    op.alter_column("cgr_cinema_details", "password", existing_type=sa.TEXT(), nullable=True)
