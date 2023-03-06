"""rename_permission_advanced_pro_support
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "a8e0474a749c"
down_revision = "af95cd1b1a41"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE permission SET name = 'MOVE_SIRET' WHERE name = 'ADVANCED_PRO_SUPPORT'")


def downgrade() -> None:
    op.execute("UPDATE permission SET name = 'ADVANCED_PRO_SUPPORT' WHERE name = 'MOVE_SIRET'")
