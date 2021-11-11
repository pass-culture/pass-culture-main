"""Validate new constraint on `payment` table

Revision ID: 2a4bf5f4d9c2
Revises: 558aec8c0580
Create Date: 2021-06-07 20:45:11.504545

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "2a4bf5f4d9c2"
down_revision = "558aec8c0580"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE payment VALIDATE CONSTRAINT payment_reimbursement_constraint")


def downgrade():
    pass
