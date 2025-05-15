"""Add user_account_update_request.dsTechnicalId"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "0fcad96c98ba"
down_revision = "1e2330f8af48"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("user_account_update_request", sa.Column("dsTechnicalId", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("user_account_update_request", "dsTechnicalId")
