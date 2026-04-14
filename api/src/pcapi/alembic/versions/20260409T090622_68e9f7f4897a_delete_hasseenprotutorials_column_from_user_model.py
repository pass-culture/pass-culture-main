"""delete hasSeenProTutorials column from user model"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "68e9f7f4897a"
down_revision = "edc44f1d889e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("user", "hasSeenProTutorials")


def downgrade() -> None:
    op.add_column(
        "user",
        sa.Column(
            "hasSeenProTutorials", sa.BOOLEAN(), server_default=sa.text("false"), autoincrement=False, nullable=True
        ),
    )
