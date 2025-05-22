"""Add stock.offererAddressId FK constraint"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3de57d5476d5"
down_revision = "fe5b67e9e72b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_foreign_key(
        "stock_offererAddressId_fkey",
        "stock",
        "offerer_address",
        ["offererAddressId"],
        ["id"],
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("stock_offererAddressId_fkey", "stock", type_="foreignkey")
