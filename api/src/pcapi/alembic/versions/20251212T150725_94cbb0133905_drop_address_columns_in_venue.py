"""Drop address columns in venue table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "94cbb0133905"
down_revision = "f2c8dc495880"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("venue", "latitude")
    op.drop_column("venue", "departementCode")
    op.drop_column("venue", "longitude")


def downgrade() -> None:
    op.add_column("venue", sa.Column("longitude", sa.NUMERIC(precision=8, scale=5), autoincrement=False, nullable=True))
    op.add_column("venue", sa.Column("departementCode", sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column("venue", sa.Column("latitude", sa.NUMERIC(precision=8, scale=5), autoincrement=False, nullable=True))
