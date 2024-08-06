"""
add cancellationUser for booking
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "f189cd721831"
down_revision = "35d67a2cddcd"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("booking", sa.Column("cancellationUserId", sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column("booking", "cancellationUserId")
