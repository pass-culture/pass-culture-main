"""migrate activity triggers

Revision ID: 09857d7d7492
Revises: 253b0a83eead
Create Date: 2019-06-05 09:23:25.550390

"""
from alembic import op
from postgresql_audit.base import VersioningManager

# revision identifiers, used by Alembic.
from pcapi.core.offers.models import Mediation


revision = "09857d7d7492"
down_revision = "253b0a83eead"
branch_labels = None
depends_on = None


def upgrade():
    versioned_tables_to_migrate = [
        "offerer",
        "venue",
        "offer",
        "stock",
        "booking",
        "mediation",
        "product",
        "bank_information",
        "venue_provider",
    ]
    for table_name in versioned_tables_to_migrate:
        op.execute(f'DROP TRIGGER IF EXISTS audit_trigger_row ON "{table_name}";')

    versioning_manager = VersioningManager(schema_name="public")
    versioning_manager.create_audit_table(Mediation.__table__, op.get_bind())

    for table_name in versioned_tables_to_migrate:
        op.execute(
            f"""
            SELECT public.audit_table(oid) 
            FROM pg_class 
            WHERE oid = '{table_name}'::regclass;
        """
        )


def downgrade():
    pass
