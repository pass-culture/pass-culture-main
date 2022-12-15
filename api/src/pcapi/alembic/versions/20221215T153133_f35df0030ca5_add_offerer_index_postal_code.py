"""Add_Offerer_index_postal_code
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "f35df0030ca5"
down_revision = "aca83eb30235"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(op.f("ix_offerer_postalCode"), "offerer", ["postalCode"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_offerer_postalCode"), table_name="offerer")
