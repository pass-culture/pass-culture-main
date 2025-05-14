"""Add NOT NULL constraint on "offerer.siren" (step 2 of 4)"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "080d052208f3"
down_revision = "0eb9b57f216c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout = '300s'")
        op.execute('ALTER TABLE "offerer" VALIDATE CONSTRAINT "offerer_siren_not_null_constraint"')
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
