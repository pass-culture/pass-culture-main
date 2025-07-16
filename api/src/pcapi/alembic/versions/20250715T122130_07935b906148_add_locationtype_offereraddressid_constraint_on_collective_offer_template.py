"""
add locationType/offererAddressId constraint on collective_offer_template
"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "07935b906148"
down_revision = "185416119576"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "collective_offer" DROP CONSTRAINT IF EXISTS "collective_offer_location_type_offerer_address_constraint";
        ALTER TABLE "collective_offer" ADD CONSTRAINT "collective_offer_location_type_offerer_address_constraint"
        CHECK (
            "locationType" IS NOT NULL
            AND (
                ("locationType" = 'ADDRESS' AND "offererAddressId" IS NOT NULL)
                OR ("locationType" <> 'ADDRESS' AND "offererAddressId" IS NULL)
            )
        ) NOT VALID;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE "collective_offer" DROP CONSTRAINT IF EXISTS "collective_offer_location_type_offerer_address_constraint";
        """
    )
