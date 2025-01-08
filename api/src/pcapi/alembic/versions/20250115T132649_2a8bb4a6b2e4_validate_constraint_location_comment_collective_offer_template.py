"""
Validate check constraint on locationComment for collective offer template
"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2a8bb4a6b2e4"
down_revision = "c62c5ad8c2a1"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout = '300s'")
        op.execute(
            'ALTER TABLE "collective_offer_template" VALIDATE CONSTRAINT "collective_offer_tmpl_location_comment_constraint"'
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
