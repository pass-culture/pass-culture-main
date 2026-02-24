"""for dev 2"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = 'ebba1a03bb13ee9'
down_revision = 'c329da08a0ab'
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE achievement RENAME COLUMN foo TO bar ")


def downgrade() -> None:
    op.execute("ALTER TABLE achievement RENAME COLUMN bar TO foo ")
