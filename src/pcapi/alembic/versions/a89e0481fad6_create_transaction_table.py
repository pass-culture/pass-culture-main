"""create transaction table

Revision ID: a89e0481fad6
Revises: a6bdec6dde59
Create Date: 2019-06-12 13:15:26.579574

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
# revision identifiers, used by Alembic.
from sqlalchemy.engine.reflection import Inspector


revision = 'a89e0481fad6'
down_revision = 'a6bdec6dde59'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    if "transaction" not in tables:
        op.create_table(
            'transaction',
            sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
            sa.Column('native_transaction_id', sa.BigInteger),
            sa.Column('issued_at', sa.DateTime(timezone=False)),
            sa.Column('client_addr', postgresql.INET),
            sa.Column('actor_id', sa.BigInteger)
        )

def downgrade():
    pass
