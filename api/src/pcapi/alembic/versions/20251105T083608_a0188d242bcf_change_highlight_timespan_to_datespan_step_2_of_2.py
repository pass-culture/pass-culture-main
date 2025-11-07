"""Change highlight timespan to datespan step 2 of 2
Rename colums from timespan to datespan"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "a0188d242bcf"
down_revision = "b1b0355dabed"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute(sa.text("""ALTER TABLE highlight RENAME COLUMN availability_timespan TO availability_datespan;"""))
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute(sa.text("""ALTER TABLE highlight RENAME COLUMN highlight_timespan TO highlight_datespan;"""))


def downgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute(sa.text("""ALTER TABLE highlight RENAME COLUMN availability_datespan TO availability_timespan;"""))
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute(sa.text("""ALTER TABLE highlight RENAME COLUMN highlight_datespan TO highlight_timespan;"""))
