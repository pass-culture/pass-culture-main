"""Add settlement_batch.externalId"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "fb2fd1a4a0cd"
down_revision = "d0d19beab7b1"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("settlement_batch", sa.Column("externalId", sa.Text(), nullable=False))


def downgrade() -> None:
    op.drop_column("settlement_batch", "externalId")
