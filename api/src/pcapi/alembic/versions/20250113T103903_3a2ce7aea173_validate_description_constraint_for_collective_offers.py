"""
Validate description constraint for collective_offers
"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3a2ce7aea173"
down_revision = "1246db03a74c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout = '300s'")
        op.execute('ALTER TABLE "collective_offer" VALIDATE CONSTRAINT "collective_offer_description_constraint"')
        op.execute(
            'ALTER TABLE "collective_offer_template" VALIDATE CONSTRAINT "collective_offer_tmpl_description_constraint"'
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
