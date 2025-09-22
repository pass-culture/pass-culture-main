"""Add NOT NULL constraint on "custom_reimbursement_rule.timespan" (step 2 of 4)"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b30548c33fbc"
down_revision = "8bde99f23973"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout = '300s'")
        op.execute(
            'ALTER TABLE "custom_reimbursement_rule" VALIDATE CONSTRAINT "custom_reimbursement_rule_timespan_not_null_constraint"'
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
