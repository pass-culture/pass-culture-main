"""Add concurrent index on CollectiveOffer.offererAddressId
"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "70592d8848a0"
down_revision = "fb85525c4817"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            op.f("ix_collective_offer_offererAddressId"),
            "collective_offer",
            ["offererAddressId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_collective_offer_offererAddressId"),
            table_name="collective_offer",
            postgresql_concurrently=True,
            if_exists=True,
        )
