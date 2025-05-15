"""
Drop column  beginningDatetime
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c34443975234"
down_revision = "f84fb33f512c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("collective_stock", "beginningDatetime")


def downgrade() -> None:
    op.add_column("collective_stock", sa.Column("beginningDatetime", sa.DateTime(), index=False, nullable=True))
