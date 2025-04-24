"""Add NOT NULL constraint on "offer.productId" VALIDATE step"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "021efec9912b"
down_revision = "d565d2035871"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    # Theses migrations have already been executed in staging and prod
    if settings.IS_PROD or settings.IS_STAGING:
        pass
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout = '2600s'")
        op.execute('ALTER TABLE "offer" VALIDATE CONSTRAINT "check_offer_linked_to_product_constraint"')
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
