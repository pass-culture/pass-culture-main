"""add_number_of_tickets_to_stock_model_for_eac_collective_offers
"""
from alembic import op
import sqlalchemy as sa


revision = "503904c2cab7"
down_revision = "1ab309876ab0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("stock", sa.Column("numberOfTickets", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("stock", "numberOfTickets")
