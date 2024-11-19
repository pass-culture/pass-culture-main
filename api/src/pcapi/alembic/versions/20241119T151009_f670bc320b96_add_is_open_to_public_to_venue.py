"""
Add isOpenToPublic to venue
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "f670bc320b96"
down_revision = "b5c2c74ed9e5"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("venue", sa.Column("isOpenToPublic", sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column("venue", "isOpenToPublic")
