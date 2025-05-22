"""Create index: email_domain(user.email)"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9803f6ec13df"
down_revision = "ffc1d7402c8a"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        # Tested on staging: 58 seconds
        op.execute("SET SESSION statement_timeout='300s'")
        op.execute(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            "ix_user_email_domain" ON public."user"
            USING btree (email_domain(email));
            """
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            index_name="ix_user_email_domain",
            table_name="user",
            postgresql_concurrently=True,
            if_exists=True,
        )
