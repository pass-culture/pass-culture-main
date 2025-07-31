"""Add NOT NULL constraint on "artist.is_blacklisted" (step 2 of 4)"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a538858d9a48"
down_revision = "ca658bb4c381"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout = '300s'")
        op.execute('ALTER TABLE "artist" VALIDATE CONSTRAINT "artist_is_blacklisted_not_null_constraint"')
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
