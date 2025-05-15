"""create column chronicle.externalId"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "a534059325fe"
down_revision = "8ee08df65b28"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("chronicle", sa.Column("externalId", sa.Text()))


def downgrade() -> None:
    op.drop_column("chronicle", "externalId")
