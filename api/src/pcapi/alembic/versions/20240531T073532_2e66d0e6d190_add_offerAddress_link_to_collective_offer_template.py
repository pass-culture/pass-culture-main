"""Add OffererAddress link to CollectiveOfferTemplate"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "2e66d0e6d190"
down_revision = "4b284e08940e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("""ALTER TABLE "collective_offer_template" ADD COLUMN IF NOT EXISTS "offererAddressId" BIGINT""")
    op.create_foreign_key(
        "collective_offer_template_offererAddressId_fkey",
        "collective_offer_template",
        "offerer_address",
        ["offererAddressId"],
        ["id"],
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.execute("""ALTER TABLE "collective_offer_template" DROP COLUMN IF EXISTS "offererAddressId" """)
