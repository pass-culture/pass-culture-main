"""Add NOT VALID foreign key constraint on CollectiveOffer.offererAddressId
"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "4b284e08940e"
down_revision = "7757198dbb83"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_foreign_key(
        "collective_offer_offererAddressId_fkey",
        "collective_offer",
        "offerer_address",
        ["offererAddressId"],
        ["id"],
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint(
        "collective_offer_offererAddressId_fkey",
        "collective_offer",
        type_="foreignkey",
    )
