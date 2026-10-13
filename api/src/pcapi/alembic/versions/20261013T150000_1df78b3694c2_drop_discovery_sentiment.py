"""Remove discovery sentiment in favor of emotion."""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
revision = "1df78b3694c2"
down_revision = "a47c1965b8d2"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("discovery", "sentiment")


def downgrade() -> None:
    op.add_column("discovery", sa.Column("sentiment", sa.String(), nullable=True))
