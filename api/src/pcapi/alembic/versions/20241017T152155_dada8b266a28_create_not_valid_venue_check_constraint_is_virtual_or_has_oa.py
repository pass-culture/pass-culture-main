"""Create Venue check constraint check_is_virtual_xor_has_offerer_address
"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "dada8b266a28"
down_revision = "b409480c6113"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "venue" ADD CONSTRAINT "check_is_virtual_xor_has_offerer_address" CHECK ((
            "isVirtual" IS TRUE 
            AND "offererAddressId" IS NULL
        ) OR (
            "isVirtual" IS FALSE
            AND "siret" IS NOT NULL 
            AND "offererAddressId" IS NOT NULL
        ) OR (
            "isVirtual" IS FALSE
            AND ("siret" IS NULL AND "comment" IS NOT NULL) 
            AND "offererAddressId" IS NOT NULL
        ))
        NOT VALID;
    """
    )


def downgrade() -> None:
    op.drop_constraint("check_is_virtual_xor_has_offerer_address", table_name="venue")
