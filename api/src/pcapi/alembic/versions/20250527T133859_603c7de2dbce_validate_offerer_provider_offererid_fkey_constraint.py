"""Validate `offerer_provider.offerer_provider_offererId_fkey` constraint"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "603c7de2dbce"
down_revision = "0ac13179460c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")
    op.execute("""ALTER TABLE offerer_provider VALIDATE CONSTRAINT "offerer_provider_offererId_fkey" """)
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
