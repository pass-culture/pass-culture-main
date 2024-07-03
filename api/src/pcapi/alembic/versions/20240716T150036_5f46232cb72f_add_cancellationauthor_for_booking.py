"""
add cancellationAuthor for booking
"""

from alembic import op
import sqlalchemy as sa

from pcapi import settings


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "5f46232cb72f"
down_revision = "e9caf841c7d6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    if not settings.IS_PROD:
        op.add_column("booking", sa.Column("cancellationAuthorId", sa.BigInteger(), nullable=True))


def downgrade() -> None:
    if not settings.IS_PROD:
        op.drop_column("booking", "cancellationAuthorId")
