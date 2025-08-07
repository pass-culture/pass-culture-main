"""
Add index on collective offer on locationType and offererAddressId
"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "99563d5b0706"
down_revision = "abac82d96860"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_collective_offer_locationType_offererAddressId",
            table_name="collective_offer",
            columns=["locationType", "offererAddressId"],
            unique=False,
            if_not_exists=True,
            postgresql_concurrently=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_collective_offer_locationType_offererAddressId",
            table_name="collective_offer",
            postgresql_concurrently=True,
            if_exists=True,
        )
