"""create index to search offer by provider"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "166608debd4c"
down_revision = "3de57d5476d5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("""SET SESSION statement_timeout = '900s'""")
        op.create_index(
            op.f("ix_offer_lastProviderId"),
            "offer",
            ["lastProviderId"],
            unique=False,
            postgresql_where='("lastProviderId" IS NOT NULL)',
            if_not_exists=True,
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_offer_lastProviderId"),
            table_name="offer",
            if_exists=True,
            postgresql_concurrently=True,
        )
