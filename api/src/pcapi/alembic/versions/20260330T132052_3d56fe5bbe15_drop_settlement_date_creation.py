"""drop Settlement.creationDate"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "3d56fe5bbe15"
down_revision = "17c7dd953312"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("settlement", "creationDate")


def downgrade() -> None:
    op.add_column("settlement", sa.Column("creationDate", postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
