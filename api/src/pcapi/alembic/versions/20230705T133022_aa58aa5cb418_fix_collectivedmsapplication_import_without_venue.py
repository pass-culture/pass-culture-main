"""Rework table collective_dms_application to handle dms application with unknown siret
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "aa58aa5cb418"
down_revision = "05de9b01bf9b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(op.f("ix_collective_dms_application_siret"), "collective_dms_application", ["siret"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_collective_dms_application_siret"), table_name="collective_dms_application")
