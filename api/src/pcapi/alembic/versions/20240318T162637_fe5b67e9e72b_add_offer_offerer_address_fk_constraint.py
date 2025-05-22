"""Add offer.offererAddressId FK constraint"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "fe5b67e9e72b"
down_revision = "a613c5bc707a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_foreign_key(
        "offer_offererAddressId_fkey",
        "offer",
        "offerer_address",
        ["offererAddressId"],
        ["id"],
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("offer_offererAddressId_fkey", "offer", type_="foreignkey")
