"""fill artist is_blacklisted field with default value False"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "bb820d57fd5b"
down_revision = "48519dd044d4"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("UPDATE artist SET is_blacklisted = FALSE")


def downgrade() -> None:
    op.execute("UPDATE artist SET is_blacklisted = NULL")
