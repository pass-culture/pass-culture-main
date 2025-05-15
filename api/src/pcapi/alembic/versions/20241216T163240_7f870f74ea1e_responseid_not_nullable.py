"""Set responseId not nullable for table special_event_answer"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "7f870f74ea1e"
down_revision = "8a3126f15848"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("special_event_answer", "responseId", existing_type=sa.BIGINT(), nullable=False)


def downgrade() -> None:
    op.alter_column("special_event_answer", "responseId", existing_type=sa.BIGINT(), nullable=True)
