"""Recreate index: ix_action_history_bankAccountId, with condition: not null"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8b64c0296103"
down_revision = "b2eb82127e19"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_action_history_bankAccountId",
            "action_history",
            ["bankAccountId"],
            unique=False,
            postgresql_where=sa.text('"bankAccountId" IS NOT NULL'),
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_action_history_bankAccountId",
            table_name="action_history",
            postgresql_where=sa.text('"bankAccountId" IS NOT NULL'),
            postgresql_concurrently=True,
            if_exists=True,
        )
