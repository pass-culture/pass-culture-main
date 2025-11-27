"""update session schema"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "44890ce1925d"
down_revision = "6f2f704ec485"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("user_session", sa.Column("expirationDatetime", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("user_session", "expirationDatetime")
