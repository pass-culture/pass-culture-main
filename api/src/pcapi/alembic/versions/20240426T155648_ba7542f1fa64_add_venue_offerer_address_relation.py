"""Add "offererAddressId" column to "venue" table."""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ba7542f1fa64"
down_revision = "154f5e68cb31"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("venue", sa.Column("offererAddressId", sa.BigInteger(), nullable=True))
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            op.f("ix_venue_offererAddressId"),
            "venue",
            ["offererAddressId"],
            unique=False,
            if_not_exists=True,
            postgresql_concurrently=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_venue_offererAddressId"), table_name="venue", postgresql_concurrently=True, if_exists=True
        )
    op.drop_column("venue", "offererAddressId")
