"""Drop legacy check_is_virtual_xor_has_address on venue table
"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "c4acef478bdd"
down_revision = "c59fdf213067"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("""ALTER TABLE venue DROP CONSTRAINT check_is_virtual_xor_has_address""")


def downgrade() -> None:
    op.execute(
        """
    ALTER TABLE venue ADD CONSTRAINT check_is_virtual_xor_has_address CHECK ((
        "isVirtual" IS TRUE
        AND (address IS NULL AND "postalCode" IS NULL AND city IS NULL AND "departementCode" IS NULL)
    )
    OR (
        "isVirtual" IS FALSE
        AND siret is NOT NULL
        AND ("postalCode" IS NOT NULL AND city IS NOT NULL AND "departementCode" IS NOT NULL)
    )
    OR (
        "isVirtual" IS FALSE
        AND (siret is NULL and comment is NOT NULL)
        AND (address IS NOT NULL AND "postalCode" IS NOT NULL AND city IS NOT NULL AND "departementCode" IS NOT NULL)
    )) NOT VALID;
    """
    )
