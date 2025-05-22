"""Set questionId not nullable for table special_event_answer"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "723ca088adc4"
down_revision = "7f870f74ea1e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("special_event_answer", "questionId", existing_type=sa.BIGINT(), nullable=False)


def downgrade() -> None:
    op.alter_column("special_event_answer", "questionId", existing_type=sa.BIGINT(), nullable=True)
