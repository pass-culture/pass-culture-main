"""Create index: ix_offer_venueId_subcategoryId"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "442b05ddc75e"
down_revision = "7c153c465a5a"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout=0")
        op.create_index(
            "ix_offer_venueId_subcategoryId",
            "offer",
            ["venueId", "subcategoryId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_offer_venueId_subcategoryId",
            table_name="offer",
            postgresql_concurrently=True,
            if_exists=True,
        )
