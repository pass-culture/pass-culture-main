"""add end_import_data column to special_event table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "c2065c857c35"
down_revision = "b82597ef665d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("special_event", sa.Column("endImportDate", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("special_event", "endImportDate")
