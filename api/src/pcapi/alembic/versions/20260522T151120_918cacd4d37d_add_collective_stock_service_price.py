"""Add servicePrice to collective_stock"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "918cacd4d37d"
down_revision = "b5f85a536ef6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("collective_stock", sa.Column("servicePrice", sa.Numeric(precision=10, scale=2), nullable=True))


def downgrade() -> None:
    op.drop_column("collective_stock", "servicePrice")
