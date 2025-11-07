"""Add period to educational_deposit"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "3c967a1782c0"
down_revision = "0cebf2b2aac6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("educational_deposit", sa.Column("period", postgresql.TSRANGE(), nullable=True))


def downgrade() -> None:
    op.drop_column("educational_deposit", "period")
