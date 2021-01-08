"""Remove check constraint on payment.recipientName (Step 4/4 to add not null constraint)

Revision ID: 77c4edf7c1fe
Revises: 9e677288a5a3
Create Date: 2021-01-08 09:53:36.202215

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "77c4edf7c1fe"
down_revision = "9e677288a5a3"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("recipient_name_not_null_constraint", table_name="payment")


def downgrade():
    op.execute(
        """
            ALTER TABLE payment ADD CONSTRAINT recipient_name_not_null_constraint CHECK ("recipientName" IS NOT NULL) NOT VALID;
        """
    )
