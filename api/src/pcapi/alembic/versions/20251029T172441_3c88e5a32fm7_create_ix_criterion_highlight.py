"""Add column to criterion table: highlightId"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3c88e5a32fm7"
down_revision = "2b8eb6b584c3"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            op.f("ix_criterion_highlightId"),
            "criterion",
            ["highlightId"],
            if_not_exists=True,
            postgresql_concurrently=True,
            unique=False,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_criterion_highlightId"),
            table_name="criterion",
            if_exists=True,
            postgresql_concurrently=True,
        )
