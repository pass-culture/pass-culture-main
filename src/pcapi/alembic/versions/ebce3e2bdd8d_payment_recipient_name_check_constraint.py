"""Add check_constraint on payment.recipientName (Step 1/4 to add not null constraint)

Revision ID: ebce3e2bdd8d
Revises: 0784847b5e46
Create Date: 2021-01-08 09:42:57.931338

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "ebce3e2bdd8d"
down_revision = "0784847b5e46"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
            ALTER TABLE payment ADD CONSTRAINT recipient_name_not_null_constraint CHECK ("recipientName" IS NOT NULL) NOT VALID;
        """
    )


def downgrade():
    op.drop_constraint("recipient_name_not_null_constraint", table_name="payment")
