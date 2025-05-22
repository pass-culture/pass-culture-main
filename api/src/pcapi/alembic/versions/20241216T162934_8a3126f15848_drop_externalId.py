"""drop externalId column in special_operation_answer table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8a3126f15848"
down_revision = "3a2ce7aea173"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("special_event_answer", "externalId")


def downgrade() -> None:
    op.add_column("special_event_answer", sa.Column("externalId", sa.TEXT(), autoincrement=False, nullable=False))
