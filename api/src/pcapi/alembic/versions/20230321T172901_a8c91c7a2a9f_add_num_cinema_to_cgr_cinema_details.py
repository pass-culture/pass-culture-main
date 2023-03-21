"""add_num_cinema_to_cgr_cinema_details
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "a8c91c7a2a9f"
down_revision = "bf927d0e97e8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("cgr_cinema_details", sa.Column("numCinema", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("cgr_cinema_details", "numCinema")
