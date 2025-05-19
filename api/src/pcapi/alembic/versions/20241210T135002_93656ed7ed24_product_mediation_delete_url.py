"""Delete production.url column (2/2)"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "93656ed7ed24"
down_revision = "9803f6ec13df"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("product_mediation", "url")


def downgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.add_column("product_mediation", sa.Column("url", sa.VARCHAR(length=255), autoincrement=False, nullable=True))
