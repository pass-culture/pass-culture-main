"""Add settlement creationDate column"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "4395343a5323"
down_revision = "f10db8706ca5"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("settlement", sa.Column("creationDate", sa.DateTime(), nullable=False))


def downgrade() -> None:
    op.drop_column("settlement", "creationDate")
