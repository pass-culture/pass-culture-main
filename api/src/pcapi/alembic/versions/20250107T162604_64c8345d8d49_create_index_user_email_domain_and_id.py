"""Create index: ix_user_email_domain_and_id"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "64c8345d8d49"
down_revision = "1c267d0a5fb9"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='600s'")
        op.execute(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            "ix_user_email_domain_and_id" ON public."user"
            USING btree (email_domain(email), id);
            """
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            index_name="ix_user_email_domain_and_id",
            table_name="user",
            postgresql_concurrently=True,
            if_exists=True,
        )
