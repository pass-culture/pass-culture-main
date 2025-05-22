"""
add price index on stock
"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2eee70a08b61"
down_revision = "e82695d3ec03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("""SET SESSION statement_timeout = '900s'""")
        op.create_index(
            op.f("ix_stock_price"), "stock", ["price"], unique=False, if_not_exists=True, postgresql_concurrently=True
        )
        op.execute(
            f"""
                SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
            """
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(op.f("ix_stock_price"), table_name="stock", if_exists=True, postgresql_concurrently=True)
