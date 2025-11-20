"""Create biography field in Artist"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "42c9f5add3a3"
down_revision = "62fa496efa1b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("artist", sa.Column("biography", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("artist", "biography")
