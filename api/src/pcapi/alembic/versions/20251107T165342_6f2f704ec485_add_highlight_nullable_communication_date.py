"""Add new nullable communication_date in table highlight"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "6f2f704ec485"
down_revision = "42c9f5add3a3"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("highlight", sa.Column("communication_date", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("highlight", "communication_date")
