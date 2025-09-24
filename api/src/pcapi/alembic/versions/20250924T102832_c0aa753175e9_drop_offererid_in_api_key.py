"""Drop offererId column in ApiKey"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c0aa753175e9"
down_revision = "c69e2d3f4f73"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_api_key_offererId"),
            table_name="api_key",
            postgresql_concurrently=True,
            if_exists=True,
        )
    op.drop_column("api_key", "offererId")


def downgrade() -> None:
    op.add_column("api_key", sa.Column("offererId", sa.BIGINT(), autoincrement=False, nullable=True))
