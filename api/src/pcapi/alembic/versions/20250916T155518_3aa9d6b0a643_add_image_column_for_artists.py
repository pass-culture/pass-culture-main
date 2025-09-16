"""Add column for computed image in artist table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "3aa9d6b0a643"
down_revision = "63512bb0a518"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("artist", sa.Column("computed_image", sa.TEXT(), nullable=True))


def downgrade() -> None:
    op.drop_column("artist", "computed_image")
