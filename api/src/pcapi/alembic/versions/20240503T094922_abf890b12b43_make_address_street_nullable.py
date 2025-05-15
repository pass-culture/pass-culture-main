"""Make Address.street column nullable"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "abf890b12b43"
down_revision = "fdb469eddd52"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("address", "street", existing_type=sa.TEXT(), nullable=True)


def downgrade() -> None:
    # We don't want to make a column not nullable in a downgrade migration
    pass
