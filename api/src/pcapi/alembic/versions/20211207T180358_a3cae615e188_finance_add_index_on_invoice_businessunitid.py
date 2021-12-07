"""Add index on Invoice.businessUnitId"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "a3cae615e188"
down_revision = "5223415d2eb7"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(op.f("ix_invoice_businessUnitId"), "invoice", ["businessUnitId"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_invoice_businessUnitId"), table_name="invoice")
