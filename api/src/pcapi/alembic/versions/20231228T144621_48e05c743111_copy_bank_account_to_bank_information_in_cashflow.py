"""
Copy "bankAccountId" to "bankInformationId" values in "cashflow" table
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "48e05c743111"
down_revision = "d727060b1531"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        update cashflow
        set "bankInformationId" = "bankAccountId"
    """
    )


def downgrade() -> None:
    pass  # Nothing to do
