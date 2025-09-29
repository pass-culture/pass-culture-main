"""Add NOT NULL constraint on "custom_reimbursement_rule.timespan" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "67857efc0589"
down_revision = "b30548c33fbc"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("custom_reimbursement_rule", "timespan", nullable=False)


def downgrade() -> None:
    op.alter_column("custom_reimbursement_rule", "timespan", nullable=True)
