"""Delete column Stock.rawProviderQuantity"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "cd92fbabf123"
down_revision = "bb820d57fd5b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("stock", "rawProviderQuantity")


def downgrade() -> None:
    # ignore squawk warning: prefer-big-int
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.add_column("stock", sa.Column("rawProviderQuantity", sa.INTEGER(), autoincrement=False, nullable=True))
