"""add an index on user_session.expirationDatetime"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "67509f8bb41b"
down_revision = "b7418384d36f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            op.f("ix_user_session_expirationDatetime"),
            "user_session",
            ["expirationDatetime"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_user_session_expirationDatetime"),
            table_name="user_session",
            postgresql_concurrently=True,
            if_exists=True,
        )
