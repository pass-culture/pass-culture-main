"""Set Settlement.batchId to nullable"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "e110c346c6c4"
down_revision = "44509d16b9bf"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.alter_column("settlement", "batchId", existing_type=sa.BIGINT(), nullable=True)


def downgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.alter_column("settlement", "batchId", existing_type=sa.BIGINT(), nullable=False)
