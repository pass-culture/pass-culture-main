"""
add locationType/offererAddressId constraint validation
"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b1ff099d46a9"
down_revision = "07935b906148"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.execute(
            'ALTER TABLE "collective_offer" VALIDATE CONSTRAINT "collective_offer_location_type_offerer_address_constraint";'
        )
        # Remettre le timeout par défaut (si settings.DATABASE_STATEMENT_TIMEOUT existe)
        op.execute("SET SESSION statement_timeout=DEFAULT")


def downgrade() -> None:
    pass
