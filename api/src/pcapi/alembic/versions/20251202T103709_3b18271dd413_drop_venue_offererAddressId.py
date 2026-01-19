"""Drop venue.offererAddressId"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3b18271dd413"
down_revision = "a445ed1268d8"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("venue", "offererAddressId")


def downgrade() -> None:
    # Can't recreate non-nullable column without data!
    op.add_column("venue", sa.Column("offererAddressId", sa.BIGINT(), autoincrement=False, nullable=True))
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_venue_offererAddressId"),
            "venue",
            ["offererAddressId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
