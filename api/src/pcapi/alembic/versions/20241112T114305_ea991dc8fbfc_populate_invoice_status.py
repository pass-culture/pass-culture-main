"""
Set all existing invoices' status as `paid`
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ea991dc8fbfc"
down_revision = "aac1de8cfaf8"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(sa.text("""UPDATE invoice SET "status" = 'paid' WHERE "status" is NULL;"""))


def downgrade() -> None:
    pass
