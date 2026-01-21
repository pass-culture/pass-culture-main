"""create artist app_search_score and pro_search_score fields"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "7c1693892cbc"
down_revision = "b2947a6863b7"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "artist",
        sa.Column(
            "app_search_score",
            sa.Float(),
            nullable=False,
            server_default="0.0",
        ),
    )
    op.add_column(
        "artist",
        sa.Column(
            "pro_search_score",
            sa.Float(),
            nullable=False,
            server_default="0.0",
        ),
    )


def downgrade() -> None:
    op.drop_column("artist", "app_search_score")
    op.drop_column("artist", "pro_search_score")
