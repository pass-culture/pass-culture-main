"""Add NOT NULL constraint on "custom_reimbursement_rule.subcategories" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b647131298f1"
down_revision = "4329988c48c8"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("custom_reimbursement_rule", "subcategories", nullable=False)


def downgrade() -> None:
    op.alter_column("custom_reimbursement_rule", "subcategories", nullable=True)
