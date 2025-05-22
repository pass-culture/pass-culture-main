"""
Add NOT NULL constraint on "offerer_address.offererId" and "offerer_address.addressId" (step 3 of 4)
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "31027ffad5ad"
down_revision = "eaeb8cfda46d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("offerer_address", "offererId", nullable=False)
    op.alter_column("offerer_address", "addressId", nullable=False)


def downgrade() -> None:
    op.alter_column("offerer_address", "offererId", nullable=True)
    op.alter_column("offerer_address", "addressId", nullable=True)
