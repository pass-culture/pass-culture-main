"""Recreate index: ix_action_history_ruleId, with condition: not null"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "51e29a607253"
down_revision = "c33860967b7e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_action_history_ruleId",
            "action_history",
            ["ruleId"],
            unique=False,
            postgresql_where=sa.text('"ruleId" IS NOT NULL'),
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_action_history_ruleId",
            table_name="action_history",
            postgresql_where=sa.text('"ruleId" IS NOT NULL'),
            postgresql_concurrently=True,
            if_exists=True,
        )
