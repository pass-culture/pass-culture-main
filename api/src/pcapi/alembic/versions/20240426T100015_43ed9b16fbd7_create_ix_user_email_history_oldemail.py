"""Create index: ix_user_email_history_oldEmail, replacing unused indexes"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "43ed9b16fbd7"
down_revision = "eccba6a07b17"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.execute(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            "ix_user_email_history_oldEmail" ON public."user_email_history"
            USING btree (("oldUserEmail" || '@' || "oldDomainEmail"));
            """
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_user_email_history_oldEmail",
            table_name="user_email_history",
            postgresql_concurrently=True,
            if_exists=True,
        )
