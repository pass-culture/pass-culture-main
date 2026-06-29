"""Add refreshTokenPayload column to single_sign_on table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "bba753156e44"
down_revision = "5dc3a149e8fa"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("single_sign_on", sa.Column("refreshTokenPayload", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("single_sign_on", "refreshTokenPayload")
