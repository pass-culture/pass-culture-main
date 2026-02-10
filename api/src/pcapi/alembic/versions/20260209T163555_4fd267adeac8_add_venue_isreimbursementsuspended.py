"""Add venue.isReimbursementSuspended"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "4fd267adeac8"
down_revision = "38afc60a955c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "venue", sa.Column("isReimbursementSuspended", sa.Boolean(), server_default=sa.text("false"), nullable=False)
    )


def downgrade() -> None:
    op.drop_column("venue", "isReimbursementSuspended")
