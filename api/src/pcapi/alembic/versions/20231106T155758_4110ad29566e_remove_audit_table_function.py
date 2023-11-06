"""Remove unused "audit_table" functions
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4110ad29566e"
down_revision = "31f16e87c3ea"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("drop function if exists public.audit_table(regclass)")
    op.execute("drop function if exists public.audit_table(regclass, text[])")


def downgrade() -> None:
    pass  # no rollback, the function really is not used
