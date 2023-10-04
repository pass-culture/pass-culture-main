"""Populate `custom_reimbursement_rule.amountInEuroCents`"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "f72b113cfe59"
down_revision = "9d9bfc829be5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
      update custom_reimbursement_rule
      set "amountInEuroCents" = (100 * amount)::integer
      where "amountInEuroCents" is null
    """
    )


def downgrade() -> None:
    pass  # nothing to do
