"""Add NOT NULL constraint on "custom_reimbursement_rule.subcategories" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "6d61c431f11b"
down_revision = "b647131298f1"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "custom_reimbursement_rule_subcategories_not_null_constraint", table_name="custom_reimbursement_rule"
    )


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "custom_reimbursement_rule" ADD CONSTRAINT "custom_reimbursement_rule_subcategories_not_null_constraint" CHECK ("subcategories" IS NOT NULL) NOT VALID"""
    )
