"""Add index on offer.authorId column"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "6993f48deb4b"
down_revision = "5da6795c25fa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute("""SET SESSION statement_timeout = '300s'""")
    op.execute(
        """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            "offer_authorId_idx" ON public.offer USING btree ("authorId")
        """
    )
    op.execute(
        f"""
            SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
        """
    )


def downgrade() -> None:
    op.drop_index(op.f("offer_authorId_idx"), table_name="offer")
