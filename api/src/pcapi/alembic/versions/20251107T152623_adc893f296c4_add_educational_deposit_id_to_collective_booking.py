"""Add educationalDepositId to collective_booking"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "adc893f296c4"
down_revision = "108c76ac8a3c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("collective_booking", sa.Column("educationalDepositId", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "collective_booking_educationalDepositId_fkey",
        "collective_booking",
        "educational_deposit",
        ["educationalDepositId"],
        ["id"],
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("collective_booking_educationalDepositId_fkey", "collective_booking", type_="foreignkey")
    op.drop_column("collective_booking", "educationalDepositId")
