"""add_password_to_cgr_cinema_details"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "4bec5e4e7ee7"
down_revision = "49ed95a60b07"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("cgr_cinema_details", sa.Column("password", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("cgr_cinema_details", "password")
