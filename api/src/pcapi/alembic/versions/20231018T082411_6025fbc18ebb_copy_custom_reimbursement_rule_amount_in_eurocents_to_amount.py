"""Copy `custom_reimbursement_rule.amountInEurocents` to `amount`
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "6025fbc18ebb"
down_revision = "00c2e096a1ac"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        update custom_reimbursement_rule
        set amount = "amountInEuroCents"
        where "amountInEuroCents" is not null
        """
    )


def downgrade() -> None:
    # See comment in the `downgrade` path of migration of 00c2e096a1ac.
    pass
