"""Add NOT NULL constraint on "collective_offer_template.locationType" (step 2 of 4)"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "be3f87ea64b1"
down_revision = "4608b67aa05f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout = '300s'")
        op.execute(
            'ALTER TABLE "collective_offer_template" VALIDATE CONSTRAINT "collective_offer_template_locationType_not_null_constraint"'
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
