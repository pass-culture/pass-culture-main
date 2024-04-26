"""Drop "address" column from "offerer" table.
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "7c7f4037358b"
down_revision = "403f300374ba"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE offerer DROP COLUMN IF EXISTS address")


def downgrade() -> None:
    op.add_column("offerer", sa.Column("address", sa.Text(), autoincrement=False, nullable=True))
