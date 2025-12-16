"""Drop venue.offererAddressId"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3b18271dd413"
down_revision = "94cbb0133905"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_venue_offererAddressId"), table_name="venue", postgresql_concurrently=True, if_exists=True
        )
    op.drop_column("venue", "offererAddressId")


def downgrade() -> None:
    # Can't recreate nullable column without data!
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
