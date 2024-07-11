"""
add cancellationAuthor for booking
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "93518cb9a7b2"
down_revision = "e0d7e16bcbaa"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("booking", sa.Column("cancellationAuthorId", sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column("booking", "cancellationAuthorId")
