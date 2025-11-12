"""Change highlight timespan to datespan step 3 of 3
Remove timerange columns"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "99b8d179336d"
down_revision = "5674186430f7"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("highlight", "availability_timespan", if_exists=True)
    op.drop_column("highlight", "highlight_timespan", if_exists=True)


def downgrade() -> None:
    op.add_column(
        "highlight", sa.Column("availability_timespan", postgresql.TSRANGE(), nullable=True), if_not_exists=True
    )
    op.add_column("highlight", sa.Column("highlight_timespan", postgresql.TSRANGE(), nullable=True), if_not_exists=True)
