"""Create index on address.postalCode (similar to deprecated offerer.postalCode)"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ae91ad1d3d2b"
down_revision = "5e5e3e71c42c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            op.f("ix_address_postalCode"),
            "address",
            ["postalCode"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(op.f("ix_address_postalCode"), table_name="address", postgresql_concurrently=True, if_exists=True)
