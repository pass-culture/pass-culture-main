"""Validate foreign key on offerer_address: offerer_address_venueId_fkey"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ae9151369f8d"
down_revision = "5ed5e8472e25"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")  # or more if needed
    op.execute("""ALTER TABLE offerer_address VALIDATE CONSTRAINT "offerer_address_venueId_fkey" """)
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
