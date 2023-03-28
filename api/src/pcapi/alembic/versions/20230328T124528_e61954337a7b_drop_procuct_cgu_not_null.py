"""Drop duplicate constraint procuct_cgu_not_null on product
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e61954337a7b"
down_revision = "8dbbae44e380"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('ALTER TABLE "product" DROP CONSTRAINT IF EXISTS "check_iscgucompatible_is_not_null";')


def downgrade() -> None:
    pass
