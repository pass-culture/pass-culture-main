"""Create partial index "ix_offer_venueId_lastProviderId_null" on "offer" table"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a4854666bc4e"
down_revision = "3f744bb45a12"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout=0")
        op.create_index(
            "ix_offer_venueId_lastProviderId_null",
            "offer",
            ["venueId"],
            unique=False,
            postgresql_where=sa.text('"lastProviderId" IS NULL'),
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout=0")
        op.drop_index(
            "ix_offer_venueId_lastProviderId_null",
            table_name="offer",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
