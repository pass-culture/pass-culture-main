"""Add optional discovery comment and emotion."""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
revision = "62b8943e7ac1"
down_revision = "3b81e9c25d60"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("discovery", sa.Column("comment", sa.Text(), nullable=True))
    op.add_column("discovery", sa.Column("emotion", sa.Text(), nullable=True))
    op.create_check_constraint(
        "check_discovery_emotion",
        "discovery",
        "emotion IN ('intrigu\u00e9', '\u00e9merveill\u00e9', 'touch\u00e9', 'surpris', 'bouscul\u00e9', 'indiff\u00e9rent')",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("check_discovery_emotion", "discovery", type_="check")
    op.drop_column("discovery", "emotion")
    op.drop_column("discovery", "comment")
