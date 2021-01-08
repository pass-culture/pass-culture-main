"""Validate check_constraint on payment.recipientName (Step 2/4 to add not null constraint)

Revision ID: 775d3270a33c
Revises: ebce3e2bdd8d
Create Date: 2021-01-08 09:48:23.061594

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "775d3270a33c"
down_revision = "ebce3e2bdd8d"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE payment VALIDATE CONSTRAINT recipient_name_not_null_constraint;")


def downgrade():
    pass
