"""Change type of `custom_reimbursement_rule.amount`: numeric -> int
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "00c2e096a1ac"
down_revision = "cbd37c328f46"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "custom_reimbursement_rule",
        "amount",
        existing_type=sa.NUMERIC(precision=10, scale=2),
        type_=sa.Integer(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "custom_reimbursement_rule",
        "amount",
        existing_type=sa.Integer(),
        type_=sa.NUMERIC(precision=10, scale=2),
        existing_nullable=True,
    )
    # This migration is followed by a second migration that copies the
    # value from `amountInEuroCents` to `amount`. Whether that second
    # migration is run or no, if we want to roll back this first
    # migration, the statement above will restore the type, but we
    # will already have lost the precision when executing the
    # `upgrade` path: the numeric value 12.34 will be truncated to the
    # integer 12. Here is the right place to restore `amount` to its
    # numeric value.
    op.execute(
        """
        update custom_reimbursement_rule
        set amount = round("amountInEuroCents"::numeric / 100, 2)
        where "amountInEuroCents" is not null
        """
    )
