"""Drop unused index: ix_user_irisFranceId"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "46e9f8e3ee4f"
down_revision = "092b7c983605"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_user_irisFranceId",
            table_name="user",
            postgresql_concurrently=True,
            if_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_user_irisFranceId",
            "user",
            ["irisFranceId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
