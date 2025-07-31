"""add is_blacklisted field to artist model"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "0ed381176cbd"
down_revision = "6418ef94834a"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "artist",
        sa.Column("is_blacklisted", sa.Boolean(), nullable=True, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("artist", "is_blacklisted")
