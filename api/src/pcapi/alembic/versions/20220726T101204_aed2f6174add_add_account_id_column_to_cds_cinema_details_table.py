"""add_account_id_column_to_cds_cinema_details_table
"""
from alembic import op
import sqlalchemy as sa


revision = "aed2f6174add"
down_revision = "5311cec32519"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("cds_cinema_details", sa.Column("accountId", sa.Text()))


def downgrade() -> None:
    op.drop_column("cds_cinema_details", "accountId")
