"""Drop "address" column from "venue" table.

"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "403f300374ba"
down_revision = "348fd34d687b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE venue DROP COLUMN IF EXISTS address")


def downgrade() -> None:
    op.add_column("venue", sa.Column("address", sa.Text(), autoincrement=False, nullable=True))
