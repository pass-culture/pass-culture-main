"""Create index on action_history."actionType" """

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c7d04bd67054"
down_revision = "0403f97207ba"


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_action_history_actionType",
            "action_history",
            ["actionType"],
            unique=False,
            postgresql_using="hash",
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_action_history_actionType",
            table_name="action_history",
            postgresql_using="hash",
            postgresql_concurrently=True,
            if_exists=True,
        )
