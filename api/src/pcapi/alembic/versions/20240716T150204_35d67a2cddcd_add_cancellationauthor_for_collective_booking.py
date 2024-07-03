"""
add cancellationAuthor for collective_booking
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "35d67a2cddcd"
down_revision = "5f46232cb72f"
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
