"""validate foreign key constarint on"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b18478ab2ea8"
down_revision = "93656ed7ed24"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute("""ALTER TABLE artist_product_link VALIDATE CONSTRAINT "artist_product_link_artist_id_fkey" """)
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
