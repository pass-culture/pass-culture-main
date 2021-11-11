"""Change and rename payment_reimbursement_constraint"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "19a51bd2cf55"
down_revision = "4317a4dc233e"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("payment_reimbursement_constraint", "payment")
    op.execute(
        """
ALTER TABLE payment
ADD CONSTRAINT reimbursement_constraint_check
CHECK (
    (
     "reimbursementRule" IS NOT NULL
     AND "reimbursementRate" IS NOT NULL
     AND "customReimbursementRuleId" IS NULL
    ) OR (
     "reimbursementRule" IS NULL
     AND "customReimbursementRuleId" IS NOT NULL
   )
)"""
    )


def downgrade():
    op.drop_constraint("reimbursement_constraint_check", "payment")
    op.execute(
        """
ALTER TABLE payment
ADD CONSTRAINT payment_reimbursement_constraint
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
)"""
    )
