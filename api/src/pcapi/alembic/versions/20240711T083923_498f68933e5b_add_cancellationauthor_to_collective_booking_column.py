"""
add cancellationAuthor for collective_booking
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "498f68933e5b"
down_revision = "93518cb9a7b2"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "collective_booking",
        sa.Column(
            "cancellationAuthorId",
            sa.BigInteger(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("collective_booking", "cancellationAuthorId")
