"""Drop pgcrypto extension
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e77d24667815"
down_revision = "1b973a88081d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("drop extension if exists pgcrypto")


def downgrade() -> None:
    op.execute("create extension if not exists pgcrypto")
