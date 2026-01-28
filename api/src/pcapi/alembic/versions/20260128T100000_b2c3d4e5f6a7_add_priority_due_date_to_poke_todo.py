"""Add priority and due_date columns to poke_todo table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "poke_todo",
        sa.Column(
            "priority",
            sa.String(length=6),
            nullable=False,
            server_default="LOW",
        ),
    )
    op.add_column(
        "poke_todo",
        sa.Column("due_date", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("poke_todo", "due_date")
    op.drop_column("poke_todo", "priority")
