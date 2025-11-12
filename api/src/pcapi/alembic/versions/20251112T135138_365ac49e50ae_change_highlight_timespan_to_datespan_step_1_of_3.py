"""Change highlight timespan to datespan step 1 of 3
Add columns daterange

INFO: The next three migrations are required only in production. Testing and staging databases are already up to date, as migrations b1b0355dabed and a0188d242bcf have been applied. These three migrations should be applied only if the columns highlight_datespan and availability_datespan do not exist, while highlight_timespan and availability_timespan do exist.
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "365ac49e50ae"
down_revision = "a0188d242bcf"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "highlight", sa.Column("highlight_datespan", postgresql.DATERANGE(), nullable=True), if_not_exists=True
    )
    op.add_column(
        "highlight", sa.Column("availability_datespan", postgresql.DATERANGE(), nullable=True), if_not_exists=True
    )


def downgrade() -> None:
    op.drop_column("highlight", "availability_datespan")
    op.drop_column("highlight", "highlight_datespan")
