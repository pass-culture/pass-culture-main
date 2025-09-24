"""Set providerId not nullable in ApiKey"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "49480744e66c"
down_revision = "c0aa753175e9"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("api_key", "providerId", existing_type=sa.BIGINT(), nullable=False)


def downgrade() -> None:
    op.alter_column("api_key", "providerId", existing_type=sa.BIGINT(), nullable=True)
