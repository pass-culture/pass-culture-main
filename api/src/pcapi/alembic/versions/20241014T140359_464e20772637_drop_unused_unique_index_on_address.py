"""Drop unused Addres.ix_complete_unique_address index"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "464e20772637"
down_revision = "c1eaf46afc44"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            index_name="ix_complete_unique_address", table_name="address", postgresql_concurrently=True, if_exists=True
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_complete_unique_address",
            "address",
            ["banId", "inseeCode", "street", "postalCode", "city", "latitude", "longitude"],
            unique=True,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
