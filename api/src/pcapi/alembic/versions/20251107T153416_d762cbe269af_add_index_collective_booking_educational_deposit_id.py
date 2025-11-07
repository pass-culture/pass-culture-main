"""Add index on collective_booking educationalDepositId"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d762cbe269af"
down_revision = "4ce0da483476"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            op.f("ix_collective_booking_educationalDepositId"),
            "collective_booking",
            ["educationalDepositId"],
            unique=False,
            if_not_exists=True,
            postgresql_concurrently=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_collective_booking_educationalDepositId"),
            table_name="collective_booking",
            if_exists=True,
            postgresql_concurrently=True,
        )
