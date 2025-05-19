"""create index ix_action_history_chronicleId"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9bca134a0476"
down_revision = "b86bf7cb97f2"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.create_index(
        "ix_action_history_chronicleId",
        "action_history",
        ["chronicleId"],
        unique=False,
        postgresql_where=sa.text('"chronicleId" IS NOT NULL'),
        if_not_exists=True,
        postgresql_concurrently=True,
    )
    op.execute("BEGIN")


def downgrade() -> None:
    op.execute("COMMIT")
    op.drop_index(
        "ix_action_history_chronicleId",
        table_name="action_history",
        postgresql_where=sa.text('"chronicleId" IS NOT NULL'),
        postgresql_concurrently=True,
        if_exists=True,
    )
    op.execute("BEGIN")
