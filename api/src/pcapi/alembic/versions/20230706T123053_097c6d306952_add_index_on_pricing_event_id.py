"""Add index on `pricing.eventId`
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "097c6d306952"
down_revision = "eb8f028d2a9c"
branch_labels = None
depends_on = None


table = "pricing"
column = "eventId"
index = "ix_pricing_eventId"


def upgrade() -> None:
    # We need to commit the transaction, because `create index
    # concurrently` cannot run inside a transaction.
    op.execute("commit")
    op.execute("set session statement_timeout = '300s'")
    op.execute(f'create index concurrently if not exists "{index}" ON {table} ("{column}")')


def downgrade() -> None:
    # We need to commit the transaction, because `drop index
    # concurrently` cannot run inside a transaction.
    op.execute("commit")
    op.execute(f'drop index concurrently if exists "{index}"')
