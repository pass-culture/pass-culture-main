"""Remove collectiveAccessInformation from venue"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "655d2fa1f6b1"
down_revision = "ad37625d13c0"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("venue", "collectiveAccessInformation")


def downgrade() -> None:
    op.add_column("venue", sa.Column("collectiveAccessInformation", sa.TEXT(), autoincrement=False, nullable=True))
