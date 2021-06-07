"""Udpate constraints on `payment` table

Revision ID: 558aec8c0580
Revises: b74c334c8095
Create Date: 2021-06-07 20:45:11.504545

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "558aec8c0580"
down_revision = "b74c334c8095"
branch_labels = None
depends_on = None


def upgrade():
    # Remove NOT NULL constraint on both columns
    op.alter_column("payment", "reimbursementRate", existing_type=sa.NUMERIC(precision=10, scale=2), nullable=True)
    op.alter_column("payment", "reimbursementRule", existing_type=sa.VARCHAR(length=200), nullable=True)
    op.execute(
        """
        ALTER TABLE payment ADD CONSTRAINT payment_reimbursement_constraint
        CHECK (
          (
            "reimbursementRule" IS NOT NULL
            AND "reimbursementRate" IS NOT NULL
            AND "customReimbursementRuleId" IS NULL
          ) OR (
            "reimbursementRule" IS NULL
            AND "reimbursementRate" IS NULL
            AND "customReimbursementRuleId" IS NOT NULL
          )
        )
        NOT VALID;
        """
    )


def downgrade():
    # Restore NOT NULL constraint on both columns. This will be slow,
    # hopefully we won't have to downgrade...
    op.alter_column("payment", "reimbursementRule", existing_type=sa.VARCHAR(length=200), nullable=False)
    op.alter_column("payment", "reimbursementRate", existing_type=sa.NUMERIC(precision=10, scale=2), nullable=False)
    op.drop_constraint("payment_reimbursement_constraint", table_name="payment")
