"""Database init

Revision ID: 5f81d0abe040
Revises: ea836848f102
Create Date: 2018-08-24 12:57:45.081918

"""
from alembic import op
import sqlalchemy as sa
import os
from pathlib import Path


# revision identifiers, used by Alembic.
revision = '5f81d0abe040'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    sql_file = Path(os.path.dirname(os.path.realpath(__file__))) / 'db_init.sql'

    data = "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO \"pass_cultur_3640\";" \
           "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO \"pass_cultur_3640\";"

    with open(sql_file, 'r') as file:
        data += file.read()
    op.execute(data)


def downgrade():
    pass
