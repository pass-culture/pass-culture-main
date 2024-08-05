"""
add cancellationauthor for booking
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "2c46ba903e87"
down_revision = "e9caf841c7d6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("booking", sa.Column("cancellationAuthorId", sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column("booking", "cancellationAuthorId")
