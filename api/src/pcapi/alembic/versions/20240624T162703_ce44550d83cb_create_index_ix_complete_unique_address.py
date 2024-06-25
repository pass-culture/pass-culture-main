"""Create index on address: ix_complete_unique_address
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ce44550d83cb"
down_revision = "036a69733891"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_complete_unique_address",
            "address",
            ["banId", "inseeCode", "street", "postalCode", "city", "latitude", "longitude"],
            unique=True,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index("ix_complete_unique_address", table_name="address", postgresql_concurrently=True, if_exists=True)
