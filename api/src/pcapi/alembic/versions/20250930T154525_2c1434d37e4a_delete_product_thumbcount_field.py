"""Delete product thumbCount field"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2c1434d37e4a"
down_revision = "ca1e0efa8036"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("product", "thumbCount")


def downgrade() -> None:
    op.add_column("product", sa.Column("thumbCount", sa.BigInteger(), nullable=False, server_default="0"))
