"""
add cancellationUser for collective booking
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "a838739fcc02"
down_revision = "f189cd721831"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "collective_booking",
        sa.Column(
            "cancellationUserId",
            sa.BigInteger(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("collective_booking", "cancellationUserId")
