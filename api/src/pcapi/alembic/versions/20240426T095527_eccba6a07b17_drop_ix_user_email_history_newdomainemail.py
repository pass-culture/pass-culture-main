"""Drop unused index: ix_user_email_history_newDomainEmail"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "eccba6a07b17"
down_revision = "f0ddc19f43e2"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_user_email_history_newDomainEmail",
            table_name="user_email_history",
            postgresql_concurrently=True,
            if_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_user_email_history_newDomainEmail",
            "user_email_history",
            ["newDomainEmail"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
