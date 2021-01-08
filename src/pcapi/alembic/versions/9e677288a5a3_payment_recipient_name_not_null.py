"""Add not null constraint on payment.recipientName (Step 3/4 to add not null constraint)

Revision ID: 9e677288a5a3
Revises: 775d3270a33c
Create Date: 2021-01-08 09:51:40.232533

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "9e677288a5a3"
down_revision = "775d3270a33c"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("payment", "recipientName", nullable=False)


def downgrade():
    op.alter_column("payment", "recipientName", nullable=True)
