"""
drop isVisibleInApp from venue
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c9e52780e038"
down_revision = "9b599c492622"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("venue", "isVisibleInApp")


def downgrade() -> None:
    op.add_column(
        "venue",
        sa.Column(
            "isVisibleInApp",
            sa.Boolean(),
            nullable=False,
            server_default=sa.sql.expression.true(),
        ),
    )
