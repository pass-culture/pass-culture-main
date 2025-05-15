"""add history chronicle link"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "8e2d25f7d65b"
down_revision = "3b79fd434823"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("action_history", sa.Column("chronicleId", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "action_history_chronicle_fkey",
        "action_history",
        "chronicle",
        ["chronicleId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("action_history_chronicle_fkey", "action_history", type_="foreignkey")
    op.drop_column("action_history", "chronicleId")
