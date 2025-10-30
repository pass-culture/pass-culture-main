"""Remove venue's isVirtual"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "7771fd024d45"
down_revision = "c23249637c33"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("venue", "isVirtual")


def downgrade() -> None:
    op.add_column(
        "venue",
        sa.Column("isVirtual", sa.BOOLEAN(), server_default=sa.text("false"), autoincrement=False, nullable=False),
    )
