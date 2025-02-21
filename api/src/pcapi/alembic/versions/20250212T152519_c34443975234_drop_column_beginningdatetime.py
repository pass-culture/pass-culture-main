"""
Drop column  beginningDatetime
"""

from alembic import op
import sqlalchemy as sa

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c34443975234"
down_revision = "6d08cf9b25c2"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("collective_stock", "beginningDatetime")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("select 1 -- squawk:ignore-next-statement")
        op.add_column("collective_stock", sa.Column("beginningDatetime", sa.DateTime(), index=False, nullable=True))

        op.execute("""SET SESSION statement_timeout = '2600s'""")
        op.execute('UPDATE collective_stock SET "beginningDatetime" = "startDatetime"')
        op.execute(
            """
                CREATE INDEX CONCURRENTLY IF NOT EXISTS
                "ix_collective_stock_beginningDatetime" ON public.collective_stock USING btree ("beginningDatetime")
            """
        )
        op.execute(
            f"""
                SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
            """
        )
