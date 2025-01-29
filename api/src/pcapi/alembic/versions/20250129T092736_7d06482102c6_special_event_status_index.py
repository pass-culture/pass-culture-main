"""add index on special_event_response status"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "7d06482102c6"
down_revision = "65d6cbee26d7"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_special_event_response_status",
            table_name="special_event_response",
            columns=["status"],
            unique=False,
            postgresql_using="hash",
            if_not_exists=True,
            postgresql_concurrently=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_special_event_response_status",
            table_name="special_event_response",
            postgresql_using="hash",
            postgresql_concurrently=True,
            if_exists=True,
        )
