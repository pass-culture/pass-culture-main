"""add_feature_flag_fnac_synchronisation_v2

Revision ID: f460dc2c9f93
Revises: None
Create Date: 2021-02-16 15:23:13.378617

"""
import os
from pathlib import Path

from alembic import op


# revision identifiers, used by Alembic.
revision = "f460dc2c9f93"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    sql_file = Path(os.path.dirname(os.path.realpath(__file__))) / "sql" / "schema_init.sql"

    with open(sql_file, "r") as file:
        data = file.read()
    op.execute(data)


def downgrade():
    pass
