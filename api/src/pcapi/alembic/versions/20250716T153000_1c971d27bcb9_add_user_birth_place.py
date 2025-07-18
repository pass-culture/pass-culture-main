"""Add birthPlace column to user table add_user_birth_place"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "1c971d27bcb9"
down_revision = "185416119576"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("user", sa.Column("birthPlace", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("user", "birthPlace")
