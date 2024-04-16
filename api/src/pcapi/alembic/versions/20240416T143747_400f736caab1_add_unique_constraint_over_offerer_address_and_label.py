"""Add OffererAddress unique constraint on offererId, addressId and label
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "400f736caab1"
down_revision = "f77615489a01"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_unique_offerer_address_per_label",
            "offerer_address",
            ["offererId", "addressId", "label"],
            unique=True,
            if_not_exists=True,
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_unique_offerer_address_per_label",
            table_name="offerer_address",
            if_exists=True,
            postgresql_concurrently=True,
        )
