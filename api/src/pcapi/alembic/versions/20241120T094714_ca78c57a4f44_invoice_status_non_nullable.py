"""
Set Invoice.status non nullable
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ca78c57a4f44"
down_revision = "c05644202f3d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("invoice", "status", existing_type=sa.TEXT(), nullable=False)


def downgrade() -> None:
    op.alter_column("invoice", "status", existing_type=sa.TEXT(), nullable=True)
