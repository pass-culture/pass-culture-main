"""Initialize database schema

Revision ID: 5f81d0abe040
Revises: ea836848f102
Create Date: 2018-08-24 12:57:45.081918

"""
import os
from pathlib import Path

from alembic import op


# revision identifiers, used by Alembic.
revision = '5f81d0abe040'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    sql_file = Path(os.path.dirname(os.path.realpath(__file__))) / 'sql' / 'schema_init.sql'

    with open(sql_file, 'r') as file:
        data = file.read()
    op.execute(data)


def downgrade():
    pass
