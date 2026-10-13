"""Ensure one discovery per user and cultural target."""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
revision = "3b81e9c25d60"
down_revision = "f4d92c76ab81"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        for target in ("work", "artist"):
            op.create_index(
                f"ix_unique_discovery_user_{target}",
                "discovery",
                ["user_id", f"{target}_id"],
                unique=True,
                postgresql_where=sa.text(f"{target}_id IS NOT NULL"),
                postgresql_concurrently=True,
                if_not_exists=True,
            )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        for target in ("artist", "work"):
            op.drop_index(
                f"ix_unique_discovery_user_{target}",
                table_name="discovery",
                postgresql_concurrently=True,
                if_exists=True,
            )
