"""Delete User.hasSeenProRgs"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "80f29f76f752"
down_revision = "1934ee3789f9"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("user", "hasSeenProRgs")


def downgrade() -> None:
    op.add_column(
        "user",
        sa.Column("hasSeenProRgs", sa.BOOLEAN(), server_default=sa.text("false"), autoincrement=False, nullable=False),
    )
