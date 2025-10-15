"""Validate siret or comment constraint on venue"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "69abcb004075"
down_revision = "762d470e2aa9"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")  # or more if needed
    op.execute("""ALTER TABLE venue VALIDATE CONSTRAINT "check_has_siret_or_comment" """)
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
