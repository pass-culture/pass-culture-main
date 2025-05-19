"""Drop `apiUrl` & `authToken` columns in provider table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b44dae2d1489"
down_revision = "64c8345d8d49"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("provider", "authToken")
    op.drop_column("provider", "apiUrl")


def downgrade() -> None:
    op.add_column("provider", sa.Column("apiUrl", sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column("provider", sa.Column("authToken", sa.VARCHAR(), autoincrement=False, nullable=True))
