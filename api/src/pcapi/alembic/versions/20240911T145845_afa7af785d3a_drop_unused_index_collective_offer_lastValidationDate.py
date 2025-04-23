"""Drop unused index on collective_offer.lastValidationDate"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "afa7af785d3a"
down_revision = "4a4fb0253a9b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.drop_index(
            "ix_collective_offer_lastValidationDate",
            table_name="collective_offer",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_collective_offer_lastValidationDate",
            "collective_offer",
            ["lastValidationDate"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
